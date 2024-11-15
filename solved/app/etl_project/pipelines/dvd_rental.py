from jinja2 import Environment, FileSystemLoader
from etl_project.connectors.postgresql import PostgreSqlClient
from etl_project.connectors.airbyte import AirbyteClient
from dotenv import load_dotenv
import os
from etl_project.assets.extract_load_transform import (
    transform,
    SqlTransform,
)
from graphlib import TopologicalSorter
from etl_project.assets.pipeline_logging import PipelineLogging
from etl_project.assets.metadata_logging import MetaDataLogging, MetaDataLoggingStatus
from sqlalchemy.exc import SQLAlchemyError

if __name__ == "__main__":
    load_dotenv()
    LOGGING_SERVER_NAME = os.environ.get("LOGGING_SERVER_NAME")
    LOGGING_DATABASE_NAME = os.environ.get("LOGGING_DATABASE_NAME")
    LOGGING_USERNAME = os.environ.get("LOGGING_USERNAME")
    LOGGING_PASSWORD = os.environ.get("LOGGING_PASSWORD")
    LOGGING_PORT = os.environ.get("LOGGING_PORT")
    TARGET_DATABASE_NAME = os.environ.get("TARGET_DATABASE_NAME")
    TARGET_SERVER_NAME = os.environ.get("TARGET_SERVER_NAME")
    TARGET_DB_USERNAME = os.environ.get("TARGET_DB_USERNAME")
    TARGET_DB_PASSWORD = os.environ.get("TARGET_DB_PASSWORD")
    TARGET_PORT = os.environ.get("TARGET_PORT")
    AIRBYTE_SERVER_NAME = os.environ.get("AIRBYTE_SERVER_NAME")
    AIRBYTE_CONNECTION_ID = os.environ.get("AIRBYTE_CONNECTION_ID")
    AIRBYTE_SECRET_KEY = os.environ.get("AIRBYTE_SECRET_KEY")

    # check env vars
    check_env_vars = all([
        LOGGING_SERVER_NAME,
        LOGGING_DATABASE_NAME,
        LOGGING_USERNAME,
        LOGGING_PASSWORD,
        LOGGING_PORT,
        TARGET_DATABASE_NAME,
        TARGET_SERVER_NAME,
        TARGET_DB_USERNAME,
        TARGET_DB_PASSWORD,
        TARGET_PORT,
        AIRBYTE_SERVER_NAME,
        AIRBYTE_CONNECTION_ID
    ])

    # Log operations of the pipeline
    pipeline_logging = PipelineLogging(
        pipeline_name="dvd_rental", log_folder_path="etl_project/logs"
    )

    try:
        assert check_env_vars
        postgresql_logging_client = PostgreSqlClient(
            server_name=LOGGING_SERVER_NAME,
            database_name=LOGGING_DATABASE_NAME,
            username=LOGGING_USERNAME,
            password=LOGGING_PASSWORD,
            port=LOGGING_PORT,
        )

        metadata_logging = MetaDataLogging(
            pipeline_name="dvd_rental", postgresql_client=postgresql_logging_client
        )


        metadata_logging.log()  # start run
        pipeline_logging.logger.info("Creating target client")
        target_postgresql_client = PostgreSqlClient(
            server_name=TARGET_SERVER_NAME,
            database_name=TARGET_DATABASE_NAME,
            username=TARGET_DB_USERNAME,
            password=TARGET_DB_PASSWORD,
            port=TARGET_PORT,
        )

        airbyte_client = AirbyteClient(
            server_name=AIRBYTE_SERVER_NAME,
            secret=AIRBYTE_SECRET_KEY
        )
        if airbyte_client.valid_connection():
            airbyte_client.trigger_sync(
                connection_id=AIRBYTE_CONNECTION_ID
            )

        transform_template_environment = Environment(
            loader=FileSystemLoader("etl_project/assets/sql/transform")
        )

        # create nodes
        staging_films = SqlTransform(
            table_name="staging_films",
            postgresql_client=target_postgresql_client,
            environment=transform_template_environment,
        )
        serving_sales_customer = SqlTransform(
            table_name="serving_sales_customer",
            postgresql_client=target_postgresql_client,
            environment=transform_template_environment,
        )
        serving_sales_cumulative = SqlTransform(
            table_name="serving_sales_cumulative",
            postgresql_client=target_postgresql_client,
            environment=transform_template_environment,
        )
        serving_sales_film = SqlTransform(
            table_name="serving_sales_film",
            postgresql_client=target_postgresql_client,
            environment=transform_template_environment,
        )
        serving_films_popular = SqlTransform(
            table_name="serving_films_popular",
            postgresql_client=target_postgresql_client,
            environment=transform_template_environment,
        )
        # create DAG
        dag = TopologicalSorter()
        dag.add(staging_films)
        dag.add(serving_sales_customer)
        dag.add(serving_sales_cumulative)
        dag.add(serving_sales_film, staging_films)
        dag.add(serving_films_popular, staging_films)
        # run transform
        pipeline_logging.logger.info("Perform transform")
        transform(dag=dag)
        pipeline_logging.logger.info("Pipeline complete")
        metadata_logging.log(
            status=MetaDataLoggingStatus.RUN_SUCCESS, logs=pipeline_logging.get_logs()
        )
        pipeline_logging.logger.handlers.clear()
    except SQLAlchemyError as e:
        pipeline_logging.logger.error(f"Pipeline failed with exception {e}")
        
       # metadata_logging.log(
           # status=MetaDataLoggingStatus.RUN_FAILURE, logs=pipeline_logging.get_logs()
        #)
        pipeline_logging.logger.handlers.clear()
    except AssertionError as e:
        pipeline_logging.logger.error(f"Pipeline failed. Ensure all "
                                      "environment variables are present")
        pipeline_logging.logger.handlers.clear()
