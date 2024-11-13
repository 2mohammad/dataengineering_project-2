# debootcamp-project2

## Objective
The objective of this ELT project is to provide insights into the DVD rental business operations, allowing stakeholders to make data-driven decisions. The data should empower users to:

Track rental trends, including popular movies and high-demand genres
Analyze customer behaviors, such as rental frequency and preferred rental formats
Monitor inventory to optimize stock and ensure availability of popular titles
Enhance marketing efforts by understanding customer demographics and preferences
Support financial planning through revenue tracking and trend analysis

##Consumers of Your Data:
The primary consumers of the data for the DVD rental database would include:

Business Analysts - For creating reports on rental performance, customer engagement, and revenue generation.
Marketing Team - To tailor marketing campaigns based on customer demographics and rental preferences.
Inventory Managers - For maintaining optimal stock levels based on rental demand patterns.
Customer Service Team - To understand and improve the customer rental experience.
Executives and Financial Planners - For high-level strategic planning, focusing on growth areas, and budget allocation.

## Questions 
- Orders and Sales
    - What is the revenue trend?
    - What are the sales performance of major countries?
- Customer Performance
    - How to segment customers?
    - What are the differences between their behaviours?

## Source datasets

#Datasets Selected:
|Data source name|URL|
|--|--|
|DVD Rental Database| https://www.postgresqltutorial.com/postgresql-getting-started/postgresql-sample-database/|
The DVD Rental Database includes the following datasets:

<img width="329" alt="image" src="https://github.com/user-attachments/assets/573f0849-66a4-4479-8fc2-3af061a5bc36">


## Solution Architecture
![Solution Architecture](images/solution-architecture.png)

## Tools Used
### 1. Postgresql
- The Northwind database is an example of an OLTP system running on PostgreSQL. It features several tables that simulate the operations of a trading company, including Customers (for customer details), Orders (tracking customer orders), Products (listing items for sale), and Suppliers (providing supplier information). We used it for analyzing the company data to answer various business questions mentioned above.


### 2. Snowflake 
- We chose to use Snowflake as our data warehouse because it offers scalable cloud-based architecture and fast query performance with separate storage and compute resources. These features make it ideal for managing and analyzing northwind datasets efficiently in order to make an analysis.

### 3. Airbyte
- Airbyte is used as a tool to extract and integrate data from our source database to our snowflake data warehouse.

### 4. DBT
- We chose DBT as our tool to transform our staging, marts, and reports tables, ensuring each table schema aligns with our designed specifications.

### 5. run_pipeline.sh as Orchestrator
- To orchestrate the integration and transformation processes, we opted to use a bash script to ensure the correct sequence of execution.

### 6. Tableau
- We chose Tableau as our BI tool to visualize and analyze our transformed data.

## Steps of Implementation
### 1. Setup Source Database
- Set up a postgresSQL datbase on AWS RDS and store its credential on AWS Secret Manager.
- Load northwind data from northwind.sql provided on northwind github repo (https://github.com/pthom/northwind_psql)

![RDS](images/rds.png)

- Change Data Capture (CDC)
    - Since we chose to use CDC, we need to tuning replication parameters on RDS by using the parameter group. Once the parameter tuning is completed, the reboot of RDS is required to make the change effective. (https://docs.aws.amazon.com/prescriptive-guidance/latest/tuning-postgresql-parameters/replication-parameters.html)
    ![cdc setp](images/cdc-setup.png)


### 2. Set up Airbyte 
- Set up airbyte on AWS EC2 and connect it by ssh
    - Launch EV2 instance with secret key 
    - Install Docker and Docker compose
    - download airbyte to EC2 by cloning the airbyte repo
    - access airbyte thourgh ssh 
![ab-ec2](images/airbyte-ec2.png)
![ab-ui](images/airbyte-ui.png)

### 3. Airbyte ELT pipeline
- In the integration module, we have a class called AirbyteClient to interact with airbyte through API.
- There is also a pipeline that trigger the connections syncs between postgres and snowflake.
- The connection credentials of airbyte resides on .env

### 4. Transform data using DBT
 - Using dimensional model to design database structure
 - Using order table as the fact table, seperate shipping information from it and combine ith other metrics to transform into dimension tables
![ERD](images/ERD.png)

### 5. Orchestration
- We create a bash file that contain execution command of both the intregration part and the transformation in the corret order.

### 6. Visulaization 
- Using tableau as visualization model
- Apply calculation metrics in it to present results
![bi_report](images/bi_report.PNG)

### 7. Schedule pipeline with ECS and ECR
- Containerize the code and its dependencies using Docker.
-  Push the Docker image to AWS ECR and establish a scheduled task in ECS to execute the Docker container, fetching the image from AWS ECR as needed.
- .env is stored on s3
![ecs](images/ecs.png)
![ecr](images/ecs.png)

## Limitations and Lessons Learned
- Building the data pipeline and transformation processes iteratively, with frequent testing, helps identify and resolve issues early in the development cycle.
- Due to an issue with the Snowflake connector in the latest Airbyte version, we need to downgrade to a previous version to resolve the problem.
- We have learned how to tune the replication log on RDS by attaching the parameter group.
- We encountered a slow syncing process in Airbyte, which was caused by full storage on RDS. We learned how to add more storage to RDS to resolve this issue.















