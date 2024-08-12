# Referral Management System - Project Plan

## 1. Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: PostgreSQL (hosted on Supabase)

## 2. Project Structure

```
referral_management_system/
│
├── app.py
├── pages/
│   ├── bill_entry.py
│   ├── wireman_management.py
│   └── bill_records.py
├── database/
│   ├── connection.py
│   └── models.py
├── utils/
│   ├── calculations.py
│   └── helpers.py
├── requirements.txt
└── README.md
```

## 3. Database Schema

We'll use PostgreSQL with the following tables:

1. `wiremen`:
   - id (PRIMARY KEY)
   - name
   - contact_info
   - date_registered

2. `bills`:
   - id (PRIMARY KEY)
   - wireman_id (FOREIGN KEY referencing wiremen.id)
   - client_name
   - amount
   - date
   - payment_status
   - points_earned

3. `points`:
   - id (PRIMARY KEY)
   - wireman_id (FOREIGN KEY referencing wiremen.id)
   - total_points
   - redeemed_points
   - balance_points

## 4. Implementation Details

### 4.1 Database Connection

Use SQLAlchemy ORM to interact with the PostgreSQL database hosted on Supabase. This will provide a clean and Pythonic way to manage database operations.

### 4.2 Page Implementation

#### 4.2.1 Bill Entry (Page 1)

- Create a form using Streamlit widgets for each field (dropdown for wireman, text input for client, number input for amount, date input for bill date, and selectbox for payment status).
- Implement form validation to ensure required fields are filled and data types are correct.
- On form submission, calculate points (1 point per Rs. 1000) and update both `bills` and `points` tables.

#### 4.2.2 Wireman Management (Page 2)

- Implement CRUD operations for wireman management.
- Create a dashboard section to display wireman statistics:
  - Use SQL aggregation functions to calculate total bills, total business, latest bill date, etc.
  - Implement point management functions (redeem all, redeem partial, reset).
- Create a filtered list of wiremen based on balance points or total bill amount.
- Implement a leaderboard using SQL ORDER BY and LIMIT clauses.

#### 4.2.3 Bill Records (Page 3)

- Implement filtering functionality using Streamlit widgets and SQL WHERE clauses.
- Display bills in a Streamlit table with update and delete options.
- Show total bill amount at the top using SQL SUM function.

### 4.3 Calculations and Helper Functions

Create utility functions in `utils/calculations.py` and `utils/helpers.py` for common operations like:
- Calculating points from bill amount
- Formatting currency and dates
- Generating SQL queries for complex operations

## 5. User Experience Improvements

1. **Responsive Design**: Ensure the Streamlit app is mobile-friendly.
2. **Dark Mode**: Implement a dark mode option for better visibility in low-light conditions.
3. **Data Visualization**: Add charts and graphs to visualize wireman performance and bill trends.
4. **Autocomplete**: Implement autocomplete for client names to reduce data entry errors.
5. **Bulk Operations**: Allow bulk updating of bills or wiremen for faster data management.
6. **Export Functionality**: Add options to export data to CSV or Excel formats.
7. **Notifications**: Implement a notification system for important events (e.g., when a wireman reaches a certain point threshold).

## 6. Development Process

1. Set up the project structure and install dependencies.
2. Implement database models and connection.
3. Create the basic Streamlit app structure with navigation.
4. Implement core functionality for each page.
5. Add data validation and error handling.
6. Implement user experience improvements.
7. Conduct thorough testing.
8. Deploy the application (e.g., on Streamlit Cloud or a VPS).

## 7. Potential Challenges and Solutions

1. **Performance**: As the database grows, queries might slow down. Implement database indexing and query optimization.
2. **Data Integrity**: Ensure all database operations are wrapped in transactions to maintain data consistency.
3. **Security**: Implement user authentication and authorization to protect sensitive data.
4. **Scalability**: Design the system to handle a growing number of wiremen and bills efficiently.