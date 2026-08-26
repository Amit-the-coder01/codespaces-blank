-- Create Employees Table
CREATE TABLE employees (
    emp_id VARCHAR(10) PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    username VARCHAR(50) UNIQUE,
    department VARCHAR(50),
    status VARCHAR(20) DEFAULT 'ACTIVE'
);

-- Insert Sample Corporate Identities
INSERT INTO employees (emp_id, first_name, last_name, email, username, department, status) VALUES
('EMP001', 'John', 'Doe', 'john.doe@corporate.local', 'jdoe', 'IT Support', 'ACTIVE'),
('EMP002', 'Jane', 'Smith', 'jane.smith@corporate.local', 'jsmith', 'Security Ops', 'ACTIVE'),
('EMP003', 'Robert', 'Johnson', 'robert.j@corporate.local', 'rjohnson', 'Finance', 'ACTIVE');