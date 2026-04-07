-- DDL : 테이블과 같이 데이터 저장소 객체를 만들거나 수정하거나 삭제할때 사용함

-- CREATE : 테이블(객체) 생성시 사용
-- 직원테이블 한글버전
CREATE TABLE 직원정보(
    직원번호 NUMBER(10),
    이름 VARCHAR2(100),
    급여 NUMBER(10) NOT NULL,
    입사일 DATE,
    부서번호 NUMBER(10)
);

-- 부서정보 테이블을 한글버전으로 만들어 주세요!
CREATE TABLE 부서정보(
    부서번호 NUMBER(10),
    부서명 VARCHAR2(100),
    매니저ID NUMBER(10),
    위치ID NUMBER(10)
);

-- 제약조건 사용법1
-- 테이블 생성시 추가한다

-- 제약조건 사용법2
-- 테이블 수정
ALTER TABLE 직원정보 ADD CONSTRAINT 직원정보_PK PRIMARY KEY(직원번호);

-- 부서정보 테이블에 부서번호 컬럼 PK 제약조건 추가
ALTER TABLE 부서정보 ADD CONSTRAINT 부서정보_PK PRIMARY KEY(부서번호);

ALTER TABLE 직원정보 ADD CONSTRAINT 직원정보_FK FOREIGN KEY(부서번호) REFERENCES 부서정보(부서번호);



-- DROP : 객체 삭제 명령
DROP TABLE 직원정보;

-- 네이버회원
CREATE TABLE 네이버회원(
    ID VARCHAR2(15),
    이름 VARCHAR2(12) NOT NULL,
    비밀번호 VARCHAR2(16),
    생년월일 DATE,
    성별 VARCHAR2(3)
);

-- 네이버블로그
CREATE TABLE 네이버블로그(
    블로그번호 NUMBER(10),
    블로그제목 VARCHAR2(100) NOT NULL,
    블로그내용 VARCHAR2(4000),
    ID VARCHAR2(15)
);

-- 1번
ALTER TABLE 네이버회원 ADD CONSTRAINT 회원_ID_PK PRIMARY KEY(ID);
-- 2번
ALTER TABLE 네이버회원 ADD CONSTRAINT 회원_성별_CK CHECK(성별 IN ('남','여'));
-- 3번
ALTER TABLE 네이버블로그 ADD CONSTRAINT 블로그_번호_PK PRIMARY KEY(블로그번호);
-- 4번
ALTER TABLE 네이버블로그 ADD CONSTRAINT 블로그_회원ID_FK FOREIGN KEY(ID) REFERENCES 네이버회원(ID);

ALTER TABLE 네이버회원 DROP CONSTRAINT 회원_성별_CK;

DROP TABLE 네이버블로그;
DROP TABLE 네이버회원;


-- DML : 데이터 조작어
-- 테이블에 원하는 데이터를 입력/수정/삭제
-- INSERT, UPDATE, DELETE

-- INSERT : 테이블에 데이터 입력
-- 부서정보테이블에
-- IT 부서 데이터를 입력해주세요

INSERT INTO 부서정보 VALUES(10,'IT',100,1000);
INSERT INTO 부서정보 VALUES(20,'인사',1000,100);
INSERT INTO 부서정보 VALUES(30,'마케팅',100,100);
INSERT INTO 부서정보(부서번호,부서명,위치ID) VALUES(30,'IT',1000);


-- DELETE : 테이블에 있는 데이터 삭제명령
DELETE FROM 부서정보 WHERE 부서번호=20 OR 부서번호=30;

SELECT * FROM 부서정보;

-- 직원정보 테이블에 팀원 정보를 임의로 넣어주세요!
-- 팀원들이 속한 부서는 3개 이상이어야합니다1

-- SYSDATE : 현재 날짜
INSERT INTO 직원정보 VALUES(100,'승환',3000,SYSDATE,10);
INSERT INTO 직원정보 VALUES(101,'희원',3500,SYSDATE-10,20);
INSERT INTO 직원정보 VALUES(102,'승원',4000,SYSDATE-20,30);
INSERT INTO 직원정보 VALUES(103,'진영',4500,SYSDATE-30,30);
INSERT INTO 직원정보 VALUES(104,'동우',4500,SYSDATE-40,20);
INSERT INTO 직원정보 VALUES(105,'용철',4000,SYSDATE-50,10);
INSERT INTO 직원정보 VALUES(106,'근범',3500,SYSDATE-60,20);

DELETE FROM 직원정보;

-- UPDATE : 데이터 수정
UPDATE 직원정보 SET 급여=7000 WHERE 직원번호=100;
-- 입사일에 있는 데이터를 각 팀원의 생일로 바꿔주세요!
UPDATE 직원정보 SET 입사일='03/02/10' WHERE 이름='희원';
UPDATE 직원정보 SET 입사일='01/07/14' WHERE 이름='용철';
UPDATE 직원정보 SET 입사일='02/06/24' WHERE 이름='진영';
UPDATE 직원정보 SET 입사일='01/02/05' WHERE 이름='동우';
UPDATE 직원정보 SET 입사일='01/05/25' WHERE 이름='근범';
UPDATE 직원정보 SET 입사일='01/07/07' WHERE 이름='승원';


SELECT * FROM 직원정보;


COMMIT;

-- TCL : 트랜잭션 제어어
-- COMMIT, ROLLBACK
-- COMMIT : 수행한 작업을 영구히 저장할때 사용한다
SELECT * FROM 직원정보;
INSERT INTO 직원정보 VALUES(400,'해도',5000,SYSDATE,10);
DELETE FROM 직원정보;

-- DDL 명령은 AUTO COMMIT이기 때문에 주의해야 한다!
DROP TABLE 직원정보;

COMMIT;
-- ROLLBACK : 마지막 COMMIT 시점으로 되돌릴때 사용한다
ROLLBACK;

-- DCL : 데이터 제어어(권한)
-- GRANT, REVOKE

-- 상위 계정 (SYSTEM)접속
SQL> CONN SYSTEM/12345;
Connected.

-- 하위 계정(DLCTEST)생성
SQL> CREATE USER DCLTEST IDENTIFIED BY 12345;
User created.

-- 하위 계정에 접속 권한 부여
SQL> GRANT CREATE SESSION TO DCLTEST;
Grant succeeded.
 
-- 테이블 생성 권한 부여
SQL> GRANT CREATE TABLE TO DCLTEST;
Grant succeeded.

-- 테이블 공간 사용 권한 부여
SQL> GRANT UNLIMITED TABLESPACE TO DCLTEST;
Grant succeeded.
 
-- 접속 권한 회수
SQL> REVOKE CREATE SESSION FROM DCLTEST;
Revoke succeeded.

-- ROLE(권한 묶음)을 통해 권한 부여
SQL> GRANT CONNECT, RESOURCE TO DCLTEST;
Grant succeeded.



