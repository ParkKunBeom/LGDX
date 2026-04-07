-- SELECT 문법 : 데이터 조회 시 사용
-- SELECT : 어떤거를 조회할건지?
-- * : ALL
-- FROM : 어디서 데이터를 조회할건지


SELECT * FROM EMPLOYEES;
SELECT * FROM departments;
SELECT EMPLOYEE_ID FROM EMPLOYEES;

-- 부서테이블의 모든 정보를 출력해주세요!
SELECT * FROM DEPARTMENTS;

-- 직원의 사번과 급여 정보를 출력하고싶어요!
SELECT EMPLOYEE_ID, SALARY FROM EMPLOYEES;

-- 사번, FIRST_NAME, 입사일 출력해주세요
SELECT EMPLOYEE_ID, FIRST_NAME, HIRE_DATE FROM EMPLOYEES;

-- 부서번호, 부서명, 부서위치번호를 출력해주세요
SELECT DEPARTMENT_ID, DEPARTMENT_NAME, LOCATION_ID FROM DEPARTMENTS;

-- 모든 직원의 연봉을 출력해주세요!
SELECT SALARY*12 FROM EMPLOYEES;
-- Alias : 별칭
SELECT SALARY*12 AS "연봉" FROM EMPLOYEES;
SELECT SALARY*12 AS 연봉 FROM EMPLOYEES;
SELECT SALARY*12 "연봉" FROM EMPLOYEES;
SELECT SALARY*12 연봉 FROM EMPLOYEES;

-- 실행 순서
-- 1. FROM 절
-- 2. SELECT 절


-- 직원의 입사일과 입사 다음날을 출력해주세요!
SELECT HIRE_DATE AS "입사일", HIRE_DATE+1 AS "입사 다음날" 
FROM EMPLOYEES;

INSERT INTO EMPLOYEES(EMPLOYEE_ID, LAST_NAME, EMAIL, HIRE_DATE, JOB_ID) VALUES (207, '임', 'lim0606', SYSDATE,'IT_PROG');

-- where 절 : 테이블에 있는 모든행에 조건을 걸어주는 명령

-- 사번이 100인 직원의 FIRST_NAME을 출력해주세요!
SELECT FIRST_NAME 
FROM EMPLOYEES 
WHERE EMPLOYEE_ID = 100;

-- 60번째 부서에서 근무하는 직원의 사번, 급여를 출력해수세요
SELECT EMPLOYEE_ID, SALARY 
FROM EMPLOYEES 
WHERE DEPARTMENT_ID = 60;

-- 급여가 5000이하인 사람들의 사번, FIRST_NAME, 급여를 출력해주세요
SELECT EMPLOYEE_ID, FIRST_NAME, SALARY 
FROM EMPLOYEES 
WHERE SALARY <= 5000;

-- 연봉이 50000이상인 사람들의 사번, FIRST_NAME, 연봉을 출력해주세요
SELECT EMPLOYEE_ID, FIRST_NAME, SALARY*12 AS "연봉" 
FROM EMPLOYEES 
WHERE SALARY*12 >= 50000;

-- JOB_ID 가 'IT_PROG'인 직원의 사번, FIRST_NAME, JOB_ID를 출력시켜주세요
SELECT EMPLOYEE_ID, FIRST_NAME, JOB_ID 
FROM EMPLOYEES 
WHERE JOB_ID = 'IT_PROG';
-- 명령어는 대소문자 구분 안하지만 값은 대소문자를 구부한다!!

-- 부서번호가 90이고, 급여가 5000이상인 직원의 사번, FIRST_NAME 급여를 출력
SELECT EMPLOYEE_ID, FIRST_NAME, SALARY 
FROM EMPLOYEES 
WHERE DEPARTMENT_ID = 90 AND SALARY >= 5000;

-- 100번째 부서에서 근무하거나 60번째 부서에서 근무하는 직원들의
-- 사번, FIRST_NAME, 부서번호를 출력해주세요 -> OR
SELECT EMPLOYEE_ID, FIRST_NAME, DEPARTMENT_ID 
FROM EMPLOYEES 
WHERE DEPARTMENT_ID = 100 OR DEPARTMENT_ID = 60;

-- JOB_ID가 IT_PROG이 아니고, FI_ACCOUNT가 아닌 직원들의
-- 사번과 JOB_ID를 출럭해주세요
SELECT EMPLOYEE_ID, JOB_ID
FROM EMPLOYEES
WHERE JOB_ID != 'IT_PROG' AND JOB_ID != 'FI_ACCOUNT';

-- 100번째 부서에서 근무하거나 50번째 부서에서 근무하는 직원 중에서
-- 연봉이 100000이상인 직원의 사번, FIRST_NAME, 연봉을 출력해주세요
SELECT EMPLOYEE_ID, FIRST_NAME, SALARY*12 AS "연봉"
FROM EMPLOYEES
WHERE (DEPARTMENT_ID = 100 OR DEPARTMENT_ID = 50) AND SALARY*12 >= 100000;

-- IN : OR의 집합 연산
-- NOT IN : AND의 집합 (제외한다)
-- 부서번호가 30,50,90 들 중 하나인 직원의 사번, 부서번호를 출력
SELECT EMPLOYEE_ID, DEPARTMENT_ID
FROM EMPLOYEES
WHERE DEPARTMENT_ID IN (30,50,90);

-- JOB_ID가 'AD_VP'이거나 'ST_MAN'인 사람인 FIRST_NAME, JOB_ID를 출력
SELECT FIRST_NAME, JOB_ID
FROM EMPLOYEES
WHERE JOB_ID IN ('AD_VP','ST_MAN');

-- MANAGER_ID가 145,146,147,148,149가 아닌 직원의 사번과 MANAGER_ID를 출력
SELECT EMPLOYEE_ID, MANAGER_ID
FROM EMPLOYEES
WHERE MANAGER_ID NOT IN (145,146,147,148,149);

-- BETWEEN a AND b
-- 연속된 범위를 통해서 조건을 걸어줄 때 사용한다

-- 급여가 10000대인 직원의 사번과 급여를 출력해주세요
SELECT EMPLOYEE_ID, SALARY
FROM EMPLOYEES
WHERE SALARY BETWEEN 10000 AND 19999;

-- 2005년도에 입사한 직원의 이름과 입사일을 출력해주세요!
SELECT FIRST_NAME, HIRE_DATE
FROM EMPLOYEES
WHERE HIRE_DATE BETWEEN '05/01/01' AND '05/12/31';

-- 문자열 비교 검색 연산
-- LIKE 연산 % (글사주 제한X), _(글자수)
-- 와일드카드 : % , -
-- FIRST_NAME 'A'로 시작하는 직원들의 이름을 출력해주세요
SELECT FIRST_NAME
FROM EMPLOYEES
WHERE FIRST_NAME LIKE 'A%';

-- 이름이 'S'로 시작하고 'n'으로 끝나는 직원의 이름을 출력해주세요!
SELECT FIRST_NAME
FROM EMPLOYEES
WHERE FIRST_NAME LIKE 'S%n';

-- 1월에 입사한 직원의 사번과 입사일을 출력해주세요!
SELECT EMPLOYEE_ID, HIRE_DATE
FROM EMPLOYEES
WHERE HIRE_DATE LIKE '___01%';


-- GROUP BY : 그룹으로 묶어서 (집계)데이터를 조회할 때 사용한다

SELECT DEPARTMENT_ID
FROM EMPLOYEES
GROUP BY DEPARTMENT_ID;

-- 집계함수
SELECT SUM(SALARY)
FROM EMPLOYEES;

SELECT MAX(SALARY)
FROM EMPLOYEES;

-- 부서별 급여의 최소값을 출력시켜주세요!
SELECT MIN(SALARY)
FROM EMPLOYEES
GROUP BY DEPARTMENT_ID;

-- 성적표 테이블에서 학생별로 평균 점수를 출력해주세요!
-- (단, 성적이 NULL이 아닐때만)
-- IS NULL / IS NOT NULL
-- ROUND : 출력하는 소수 자리 설정
SELECT ROUND(AVG(성적),1), 학생ID
FROM 성적표
-- WHERE 성적 IS NOT NULL
GROUP BY 학생ID
HAVING AVG(성적) IS NOT NULL;

-- 과목별로 최고성적과 최저성적을 출력해주세요!
SELECT MAX(성적), MIN(성적), 과목
FROM 성적표
GROUP BY 과목;

-- 교육생정보 테이블에서 각팀에 몇 명이 있는지 출력해주세요
SELECT COUNT(학생ID), 팀
FROM 교육생정보
GROUP BY 팀;

-- 성적표 테이블에서 학생별로 파이썬을 제외한 나머지과목의 평균을 출력 해주세요!
SELECT AVG(성적), 학생ID
FROM 성적표
WHERE 과목 != 'PYTHON'
GROUP BY 학생ID;

-- HAVING : GROUP BY 로 묶여진 그룹에 조건을 걸어준다(GROUP BY 와 같이 쓰임)
-- 평균 성적이 80점 이상인 학생들만 출력하고싶어요!
-- WHERE 절에서는 집계함수 사용불가!
SELECT 학생ID
FROM 성적표
GROUP BY 학생ID
HAVING AVG(성적)>=80;

-- 교육생정보에서 소소된 팀원의 수가 3명 이상인 팀만 출력해주세요!
SELECT 팀
FROM 교육생정보
GROUP BY 팀
HAVING COUNT(학생ID)>=3;

-- 부서별 최고 연봉이 100,000이상인 부서번호를 출력해주세요
SELECT DEPARTMENT_ID, MAX(SALARY*12)
FROM EMPLOYEES
GROUP BY DEPARTMENT_ID
HAVING MAX(SALARY*12)>=100000;

-- 부서별 최고 연봉이 100 ,000이상인 부서번호 출력
SELECT DEPARTMENT_ID
FROM EMPLOYEES
GROUP BY DEPARTMENT_ID
HAVING MAX(SALARY*12)>=100000;


-- ORDER BY : 특정 컬럼으로 정렬(SELECT의 구조중 제일 마지막에 실행시킨다)
SELECT DEPARTMENT_ID, MAX(SALARY*12) AS "최고연봉"
FROM EMPLOYEES
GROUP BY DEPARTMENT_ID
HAVING MAX(SALARY*12)>=100000
ORDER BY 최고연봉 DESC;

-- JOIN : 두개 이상의 테이블에서 데이터를 조회하는 방법
-- CROSS JOIN : 두개의 테이블에서 모든 경우의 수로 데이터를 출력하겠습니다

-- 전직원의 FIRST NAME , 부서이름을 출력해주세요
-- 조인조건 : EMPLOYEES.DEPARTMENT ID = DEPARTMENTS. DEPARTMENT ID
SELECT FIRST_NAME, DEPARTMENT_NAME, d.DEPARTMENT_ID
FROM DEPARTMENTS d, EMPLOYEES e
WHERE e.DEPARTMENT_ID = d.DEPARTMENT_ID;

-- 사번이 100인 직원의 FIRST_NAME, 부서 이름을 출력
SELECT E.FIRST_NAME, D.DEPARTMENT_NAME
FROM EMPLOYEES E, DEPARTMENTS D
WHERE E.DEPARTMENT_ID = D.DEPARTMENT_ID AND E.EMPLOYEE_ID = 100;

-- 60번째 부서에서 근무하는 직원 중 5000이상의 급여를 받는 직원의
-- 이름, 부서명, 급여 출력
SELECT FIRST_NAME, DEPARTMENT_NAME, SALARY
FROM EMPLOYEES e,DEPARTMENTS d
where e.department_id=60 and salary>=5000 and e.department_id= d.department_id;

-- 각 부서의 부서장 사번과, FIRST_NAME, 급여, 부서이름을 출력
SELECT E.EMPLOYEE_ID, E.FIRST_NAME, E.SALARY, D.DEPARTMENT_NAME
FROM EMPLOYEES E, DEPARTMENTS D
WHERE D.MANAGER_ID = E.EMPLOYEE_ID;

-- DEPARTMNETS, LOCATIONS, COUNTRIES 테이블을 이용해서
-- 각 부서의 이름, 부서가 위치한 도시이름, 나라이름을 출력
SELECT DEPARTMENT_NAME, CITY, COUNTRY_NAME
FROM DEPARTMENTS D, LOCATIONS L, COUNTRIES C
WHERE D.LOCATION_ID = L.LOCATION_ID AND L.COUNTRY_ID = C.COUNTRY_ID;

-- 서브쿼리 : 쿼리문안에서 사용되어지는 또다른 쿼리문

-- Neena라는 직원과 같은 부서에서 근무하는 직원들의
-- FIRST_NAME, 급여, 부서번호 출력
SELECT FIRST_NAME, SALARY, DEPARTMENT_ID
FROM EMPLOYEES 
WHERE DEPARTMENT_ID = (SELECT DEPARTMENT_ID
                         FROM EMPLOYEES
                         WHERE FIRST_NAME='Neena');

-- Neena의 부서번호를 구해줘
SELECT DEPARTMENT_ID 
FROM EMPLOYEES 
WHERE FIRST_NAME = 'Neena';

-- FIRST_NAME 이 'shelli'인 직원보다 급여가 낮은 직원의 이름, 급여 출력
SELECT FIRST_NAME, SALARY
FROM EMPLOYEES
WHERE SALARY <(SELECT SALARY
               FROM EMPLOYEES
               WHERE FIRST_NAME = 'Shelli');

-- Nancy 보다 빨리 입사한 직원의 사번과 이름, 입사일을 출력
SELECT EMPLOYEE_ID, FIRST_NAME, HIRE_DATE
FROM EMPLOYEES
WHERE HIRE_DATE<(SELECT HIRE_DATE
                 FROM EMPLOYEES
                 WHERE FIRST_NAME='Nancy');

-- 전직원의 평균급여보다 더 많이 받는 직원의 이름, 급여를 출력해주세요
SELECT FIRST_NAME, SALARY
FROM EMPLOYEES
WHERE SALARY>(SELECT AVG(SALARY)
              FROM EMPLOYEES);

-- 'IT'부서에서 근무하는 직원의 사번, 이름, 부서번호를 출력해주세요
SELECT EMPLOYEE_ID, FIRST_NAME, DEPARTMENT_ID
FROM EMPLOYEES
WHERE DEPARTMENT_ID=(SELECT DEPARTMENT_ID
                     FROM DEPARTMENTS
                     WHERE DEPARTMENT_NAME='IT');
                     
SELECT DEPARTMENT_NAME
FROM DEPARTMENTS
WHERE DEPARTMENT_NAME='IT';

-- 'IT'부서와 'Sales' 부서에서 근무하는 직원들의
-- 사번, 이름, 급여, 부서번호를 출력해주세요
SELECT EMPLOYEE_ID, FIRST_NAME, SALARY, DEPARTMENT_ID
FROM EMPLOYEES
WHERE DEPARTMENT_ID in (SELECT DEPARTMENT_ID
                     FROM DEPARTMENTS
                     WHERE DEPARTMENT_NAME='IT' OR DEPARTMENT_NAME='Sales');
                     
-- LAST_NAME이 'King' 또는 'Kochhar'인 직원들과 같은 부서에서 근무하는
-- 직원의 사번, FIRST_NAME, 부서 번호를 출럭해주세요
SELECT EMPLOYEE_ID, FIRST_NAME, DEPARTMENT_ID
FROM EMPLOYEES
WHERE DEPARTMENT_ID IN (SELECT DEPARTMENT_ID
                        FROM EMPLOYEES
                        WHERE LAST_NAME IN ('King', 'Kochhar'));
                        
-- 'IT' 부서의 직원들과 같은 급여를 받는 직원의
-- 사번, 이름, 급여, 부서번호를 출력해주세요
SELECT EMPLOYEE_ID, FIRST_NAME, SALARY, DEPARTMENT_ID
FROM EMPLOYEES
WHERE SALARY IN (SELECT SALARY
                 FROM EMPLOYEES
                 WHERE DEPARTMENT_ID = (SELECT DEPARTMENT_ID
                                        FROM DEPARTMENTS
                                        WHERE DEPARTMENT_NAME='IT'));

-- 다중행 다중열 서브쿼리                                        
-- 각 부서별 최고 급여를 받는 직원의 사번, 이름, 급여, 부서번호를 출력해주세요
SELECT EMPLOYEE_ID, FIRST_NAME, SALARY, DEPARTMENT_ID
FROM EMPLOYEES
WHERE (SALARY, DEPARTMENT_ID) IN (SELECT MAX(SALARY), DEPARTMENT_ID
                                  FROM EMPLOYEES
                                  GROUP BY DEPARTMENT_ID);
                                 
                                 
-- ANY, ALL 크기 비교 연산
-- ANY : 하나라도 만족한다면 (OR)
-- ALL : 전부다 만족할때만 (AND)
-- 'IT' 부서의 급여보다 더 많은 받는 직원의
-- 이름, 급여, 부서번호를 출력해주세요!
SELECT FIRST_NAME, SALARY, DEPARTMENT_ID
FROM EMPLOYEES
WHERE SALARY > ALL(SELECT SALARY
                   FROM EMPLOYEES
                   WHERE DEPARTMENT_ID = 60);

-- JOB_ID가 'AC_ACCOUNT'인 직원 전원보다 급여가 낮은 직원의
-- 이름, 급여를 출력해주세요
SELECT FIRST_NAME, SALARY
FROM EMPLOYEES
WHERE SALARY < ALL(SELECT SALARY
                   FROM EMPLOYEES
                   WHERE JOB_ID='AC_ACCOUNT');
                   
-- 30번 부서 직원의 급여중에서 한명이라도 높은 급여를 받을 받는 직원의
-- 사번, 급여, 부서번호를 출력해주세요ㅕ
SELECT EMPLOYEE_ID, SALARY, DEPARTMENT_ID
FROM EMPLOYEES
WHERE SALARY > ANY(SELECT SALARY
                   FROM EMPLOYEES
                   WHERE DEPARTMENT_ID=30);
                   
