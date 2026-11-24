-- HR Analytics | MySQL 8+
-- Import cleaned_data.csv into table employees (use MySQL Workbench Table Data Import Wizard).
-- Ensure EmployeeID is PRIMARY KEY. Import department_reference.csv as departments
-- and job_role_reference.csv as job_roles.

CREATE DATABASE IF NOT EXISTS hr_analytics;
USE hr_analytics;

-- Suggested employee table schema (create before CSV import if preferred)
CREATE TABLE IF NOT EXISTS employees (
 EmployeeID INT PRIMARY KEY, Age INT, Gender VARCHAR(30), Department VARCHAR(80),
 JobRole VARCHAR(80), MonthlySalary DECIMAL(10,2), Education VARCHAR(40),
 YearsExperience INT, YearsAtCompany INT, JobSatisfaction INT, Overtime VARCHAR(5),
 PerformanceRating INT, Attrition VARCHAR(5), HireYear INT, ExitYear INT NULL,
 AgeGroup VARCHAR(20), SalaryBand VARCHAR(20), ExperienceBand VARCHAR(20)
);
CREATE TABLE IF NOT EXISTS departments (
 Department VARCHAR(80) PRIMARY KEY, DepartmentLead VARCHAR(80), AnnualHiringPlan INT
);
CREATE TABLE IF NOT EXISTS job_roles (
 JobRole VARCHAR(80) PRIMARY KEY, CareerTrack VARCHAR(40)
);

-- 1. Preview records
SELECT * FROM employees LIMIT 10;

-- 2. Overall workforce KPIs
SELECT COUNT(*) AS total_employees,
 SUM(Attrition='No') AS active_employees,
 SUM(Attrition='Yes') AS employees_left,
 ROUND(100*SUM(Attrition='Yes')/COUNT(*),2) AS attrition_rate_pct
FROM employees;

-- 3. Department headcount
SELECT Department, COUNT(*) AS headcount
FROM employees GROUP BY Department ORDER BY headcount DESC;

-- 4. Department attrition rate (not just leaver count)
SELECT Department, COUNT(*) AS headcount,
 SUM(Attrition='Yes') AS leavers,
 ROUND(100*AVG(Attrition='Yes'),2) AS attrition_rate_pct
FROM employees GROUP BY Department ORDER BY attrition_rate_pct DESC;

-- 5. Department with highest attrition rate
SELECT Department, ROUND(100*AVG(Attrition='Yes'),2) AS attrition_rate_pct
FROM employees GROUP BY Department ORDER BY attrition_rate_pct DESC LIMIT 1;

-- 6. Age group attrition
SELECT AgeGroup, COUNT(*) AS employees,
 SUM(Attrition='Yes') AS leavers,
 ROUND(100*AVG(Attrition='Yes'),2) AS attrition_rate_pct
FROM employees GROUP BY AgeGroup ORDER BY attrition_rate_pct DESC;

-- 7. Gender workforce distribution
SELECT Gender, COUNT(*) AS employees,
 ROUND(100*COUNT(*)/(SELECT COUNT(*) FROM employees),2) AS workforce_share_pct
FROM employees GROUP BY Gender ORDER BY employees DESC;

-- 8. Salary band and attrition
SELECT SalaryBand, COUNT(*) AS employees,
 ROUND(100*AVG(Attrition='Yes'),2) AS attrition_rate_pct,
 ROUND(AVG(MonthlySalary),2) AS avg_monthly_salary
FROM employees GROUP BY SalaryBand ORDER BY attrition_rate_pct DESC;

-- 9. Overtime and attrition
SELECT Overtime, COUNT(*) AS employees,
 SUM(Attrition='Yes') AS leavers,
 ROUND(100*AVG(Attrition='Yes'),2) AS attrition_rate_pct
FROM employees GROUP BY Overtime;

-- 10. Job satisfaction levels and attrition
SELECT JobSatisfaction, COUNT(*) AS employees,
 ROUND(100*AVG(Attrition='Yes'),2) AS attrition_rate_pct
FROM employees GROUP BY JobSatisfaction ORDER BY JobSatisfaction;

-- 11. Percentage with low satisfaction (scores 1 or 2)
SELECT ROUND(100*SUM(JobSatisfaction IN (1,2))/COUNT(*),2) AS low_satisfaction_pct
FROM employees;

-- 12. Job roles with highest attrition
SELECT JobRole, COUNT(*) AS headcount, SUM(Attrition='Yes') AS leavers,
 ROUND(100*AVG(Attrition='Yes'),2) AS attrition_rate_pct
FROM employees GROUP BY JobRole HAVING COUNT(*) >= 10
ORDER BY attrition_rate_pct DESC;

-- 13. Average salary by department
SELECT Department, ROUND(AVG(MonthlySalary),2) AS avg_monthly_salary
FROM employees GROUP BY Department ORDER BY avg_monthly_salary DESC;

-- 14. Longest-tenured employees
SELECT EmployeeID, Department, JobRole, YearsAtCompany
FROM employees ORDER BY YearsAtCompany DESC, EmployeeID LIMIT 20;

-- 15. Experience distribution
SELECT ExperienceBand, COUNT(*) AS employees
FROM employees GROUP BY ExperienceBand ORDER BY MIN(YearsExperience);

-- 16. Performance rating distribution
SELECT PerformanceRating, COUNT(*) AS employees,
 ROUND(100*COUNT(*)/(SELECT COUNT(*) FROM employees),2) AS workforce_share_pct
FROM employees GROUP BY PerformanceRating ORDER BY PerformanceRating;

-- 17. INNER JOIN: employee count by department lead
SELECT d.DepartmentLead, e.Department, COUNT(*) AS headcount
FROM employees e INNER JOIN departments d ON e.Department=d.Department
GROUP BY d.DepartmentLead,e.Department ORDER BY headcount DESC;

-- 18. LEFT JOIN: roles including roles with no employees (if reference table has them)
SELECT r.JobRole, r.CareerTrack, COUNT(e.EmployeeID) AS headcount
FROM job_roles r LEFT JOIN employees e ON r.JobRole=e.JobRole
GROUP BY r.JobRole,r.CareerTrack ORDER BY headcount DESC;

-- 19. Subquery: employees paid above company-wide average
SELECT EmployeeID, Department, JobRole, MonthlySalary
FROM employees
WHERE MonthlySalary > (SELECT AVG(MonthlySalary) FROM employees)
ORDER BY MonthlySalary DESC;

-- 20. CTE: attrition rate by department, filtered to meaningful group sizes
WITH dept_stats AS (
 SELECT Department, COUNT(*) AS headcount,
        SUM(Attrition='Yes') AS leavers,
        AVG(Attrition='Yes') AS attrition_rate
 FROM employees GROUP BY Department
)
SELECT Department, headcount, leavers, ROUND(attrition_rate*100,2) AS attrition_rate_pct
FROM dept_stats WHERE headcount >= 20 ORDER BY attrition_rate DESC;

-- 21. Window function: rank departments by attrition
WITH dept_rates AS (
 SELECT Department, COUNT(*) AS headcount, AVG(Attrition='Yes') AS attrition_rate
 FROM employees GROUP BY Department
)
SELECT Department, headcount, ROUND(attrition_rate*100,2) AS attrition_rate_pct,
 DENSE_RANK() OVER (ORDER BY attrition_rate DESC) AS attrition_rank
FROM dept_rates;

-- 22. CASE: tenure segmentation
SELECT CASE
 WHEN YearsAtCompany <= 2 THEN '0-2 years'
 WHEN YearsAtCompany <= 5 THEN '3-5 years'
 WHEN YearsAtCompany <= 10 THEN '6-10 years'
 ELSE '10+ years' END AS tenure_group,
 COUNT(*) AS employees, ROUND(100*AVG(Attrition='Yes'),2) AS attrition_rate_pct
FROM employees GROUP BY tenure_group ORDER BY MIN(YearsAtCompany);

-- 23. Cross-analysis: overtime x satisfaction
SELECT Overtime, JobSatisfaction, COUNT(*) AS employees,
 ROUND(100*AVG(Attrition='Yes'),2) AS attrition_rate_pct
FROM employees GROUP BY Overtime, JobSatisfaction
ORDER BY Overtime, JobSatisfaction;

-- 24. Department salary versus company average
SELECT Department, ROUND(AVG(MonthlySalary),2) AS dept_avg_salary,
       ROUND((SELECT AVG(MonthlySalary) FROM employees),2) AS company_avg_salary
FROM employees GROUP BY Department;

-- 25. Attrition among high performers (descriptive, not causal)
SELECT PerformanceRating, COUNT(*) AS employees,
 SUM(Attrition='Yes') AS leavers,
 ROUND(100*AVG(Attrition='Yes'),2) AS attrition_rate_pct
FROM employees GROUP BY PerformanceRating ORDER BY PerformanceRating;
