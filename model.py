import bcrypt
import mysql.connector
from flask import (Flask, flash, make_response, redirect, render_template,
                   request, session, url_for, current_app)
import math
from flask_mail import Mail, Message
import connect
from datetime import date
# Database connection.
dbconn = None
from student.model import SixMR

def getCursor():
    global dbconn
    global connection
    if dbconn == None:
        connection = mysql.connector.connect(user=connect.dbuser,
                                             password=connect.dbpass, host=connect.dbhost,
                                             database=connect.dbname, autocommit=True)
        dbconn = connection.cursor(dictionary=True,buffered=True)
        return dbconn


cur = getCursor()


class Student:
    def __init__(self, id=None, fname=None, lname=None, enrolldate=None, address=None, phone=None, email=None, MOS=None, thesis=None, depcode=None):
        self.id = id
        self.fname = fname
        self.lname = lname
        self.enrolldate = enrolldate
        self.address = address
        self.phone = phone
        self.email = email
        self.MOS = MOS
        self.thesis = thesis
        self.depcode = depcode

    def fetch_student(self):
        sql = """select student.StudentID, concat(student.FirstName," ",student.LastName) as name, student.Email,
          student.EnrolmentDate, student.Address, student.Phone, student.ModeOfStudy, student.ThesisTitle, student.DepartmentCode,
          user.Status from student
                inner join user on student.Email = user.Email
                    order by student.StudentID;"""
        cur.execute(sql)
        studentList = cur.fetchall()
        return studentList
    
    def fetch_student_id(self, id):
        sql = """select student.StudentID, concat(student.FirstName," ",student.LastName) as name, student.Email,
          student.EnrolmentDate, student.Address, student.Phone, student.ModeOfStudy, student.ThesisTitle, student.DepartmentCode
          from student where StudentID = %s;"""
        cur.execute(sql,(id))
        studentDetail = cur.fetchall()
        return studentDetail
    
    def update_student(self, address, phone, MOS, thesis, depcode, id):
        sql = """update student set student.Address = %s, student.Phone = %s, student.ModeOfStudy = %s, student.ThesisTitle = %s, student.DepartmentCode = %s
            where StudentID = %s;"""
        cur.execute(sql,(address, phone, MOS, thesis, depcode, id))


    def insertNew(self, id, fname, lname, address, phone, email):
        sql = """INSERT INTO student (StudentID,FirstName,LastName,Address,Phone,Email) VALUES (%s, %s, %s, %s,%s, %s);"""
        cur.execute(sql, (id, fname, lname, address,
                    phone, email))



class User:
    def __init__(self, email=None, pwd=None, role=None, status=None):
        self.email = email
        self.pwd = pwd
        self.role = role
        self.status = status

    def updateStatus(self, email):
        sql = """update user set user.status = %s where user.email = %s"""
        cur.execute(sql, ('Complete profile', email))

    def rejectUser(self, email):
        sql = """delete from user where user.email = %s"""
        cur.execute(sql, (email,))

    def insertNew(self, email, pwd, role, status):
        sql = """INSERT INTO user VALUES (%s, %s, %s, %s);"""
        cur.execute(sql, (email, pwd, role, status))

    def hashPwd(self, pwd):
        # Generate a salt using bcrypt
        salt = bcrypt.gensalt()
        # Encode the password as bytes using utf-8 encoding
        bytes = pwd.encode('utf-8')
        # Hash the password using bcrypt and the generated salt
        password_hashed = bcrypt.hashpw(bytes, salt)
        # Return the hashed password
        return password_hashed


class StudentPagination:
    def __int__(self, limit=int, page=int):
        self.limit = limit
        self.page = page

    def createPagination(self, limit, page):
        offset = page*limit - limit
        sql = "select * from student"
        cur.execute(sql)
        student = cur.fetchall()
        total_row = len(student)
        total_page = math.ceil(total_row/limit)
        next = page + 1
        prev = page - 1
        sql_limit = """select student.StudentID, concat(student.FirstName," ",student.LastName) as name, student.Email,
          student.EnrolmentDate, student.Address, student.Phone, student.ModeOfStudy, student.ThesisTitle, student.DepartmentCode,
          user.Status from student
                inner join user on student.Email = user.Email
                    order by student.StudentID limit %s OFFSET %s;"""
        cur.execute(sql_limit, (limit, offset))
        studentList = cur.fetchall()
        paginationBuilder = [total_page, next, prev, studentList]
        return paginationBuilder


class Department:
    def __init__(self, code=None, name=None):
        self.code = code
        self.name = name

    def fetch_dep_list(self):
        sql = """select department.DepartmentCode, department.DepartmentName from department"""
        cur.execute(sql)
        depList = cur.fetchall()
        return depList


class Scholarship:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

    def fetch_sch_list(self):
        sql = """select scholarship.ScholarshipID, scholarship.Name from scholarship"""
        cur.execute(sql)
        schList = cur.fetchall()
        return schList


class ScholarshipRecored:
    def __init__(self, r_id=None, student_id=None, sch_id=None, tenure=None, endDate=None):
        self.r_id = r_id
        self.student_id = student_id
        self.sch_id = sch_id
        self.tenure = tenure
        self.endDate = endDate

    def insertNew(self, student_id, sch_id, tenure, endDate):
        sql = """INSERT INTO scholarshiprecord (StudentID, ScholarshipID, Tenure, EndDate)
                    VALUES (%s, %s, %s, %s);;"""
        cur.execute(sql, (student_id, sch_id, tenure, endDate))


class EmailSender:
    def __init__(self, email=None, msgContent=None):
        self.email = email
        self.msgContent = msgContent

    def sendEmail(self, email, msgContent):
        current_app.config['MAIL_SERVER'] = "smtp.gmail.com"
        current_app.config['MAIL_PORT'] = 465
        current_app.config['MAIL_USERNAME'] = "system.lupgms.lincoln@gmail.com"
        current_app.config['MAIL_PASSWORD'] = "ibqrfvzclnoksvsm"
        current_app.config['MAIL_USE_TLS'] = False
        current_app.config['MAIL_USE_SSL'] = True
        mail = Mail(current_app)
        recip = [email]
        msg = Message("Message from Lincoln University Postgraduate Monitoring System", sender="test@lincoln.com", recipients=recip)
        msg.body = msgContent
        mail.send(msg)


class Staff:
    def __init__(self, id=None):
        self.id = id

    def fetchStaff(self):
        sql = """select staff.StaffID, concat(staff.FirstName,' ', staff.LastName)as name from staff"""
        cur.execute(sql)
        staffList = cur.fetchall()
        return staffList
    
    def update_staff(self, phone, depcode, id):
        sql = """update staff set staff.Phone = %s, staff.DepartmentCode = %s
            where StaffID = %s;"""
        cur.execute(sql,(phone, depcode, id))


class EmploymentRecord:
    def __init__(self, r_id=None, student_id=None, staff_id=None, empType=None, weeklyHours=None):
        self.r_id = r_id
        self.student_id = student_id
        self.staff_id = staff_id
        self.empType = empType
        self.weeklyHours = weeklyHours

    def insertNew(self, student_id, staff_id, empType, weeklyHours):
        sql = """INSERT INTO employment (StudentID, SupervisorID, EmploymentType, WeeklyHours)
                    VALUES (%s, %s, %s, %s);;"""
        cur.execute(sql, (student_id, staff_id, empType, weeklyHours))


class Report:
    def __init__(self, report_id=None, student_id=None, role=None, dep=None, period=None, repStatus=None, clauseStr=None, studentName=None):
        self.report_id = report_id
        self.student_id = student_id
        self.role = role
        self.dep = dep
        self.period = period
        self.repStatus = repStatus
        self.clauseStr = clauseStr
        self.studentName = studentName

    def fetchReportFiltered(self, clauseStr):
        sql = f"""select student.StudentID,student.Email, student.DepartmentCode, concat(student.FirstName," ",student.LastName) as name,
              sixmr.ReportID, sixmr.ReportPeriodEndDate,sixmr.Status, sixmr.B_ReportOrder 
                from student left join sixmr on sixmr.StudentID=student.StudentID 
                 inner join user on student.Email=user.Email where user.Role='Student' and user.Status='Active' and 
                 {clauseStr}              
                 """

        cur.execute(sql)
        reports = cur.fetchall()
        return reports

    def getCurrentReportOrder(self):
        # dateOfToday = date.today()
        monthOfToday = date.today().month
        yearOfToday = date.today().year
        currentPeriod = ""
        if monthOfToday <= 6:
            currentPeriod = f"{yearOfToday}-06-30"
        else:
            currentPeriod = f"{yearOfToday}-12-31" 
        
        sql = """SELECT DATEDIFF(%s, student.EnrolmentDate) as days from student"""
        cur.execute(sql,(currentPeriod,))
        dbResult = cur.fetchone()
        days = dbResult['days']
        reportOrder = round(days/182.5)
        dbObj = {
            "currentPeriod":currentPeriod,
            "reportOrder" : reportOrder,
        }
        return dbObj
    
    def fetchexistedReportNum(self,student_id):
        
        sqlExistedReport = """select count(sixmr.StudentID) as reportNum from sixmr where sixmr.StudentID=%s"""
        cur.execute(sqlExistedReport, (student_id,))
        dbResultExistedReport = cur.fetchone()
        existedReportNum =  dbResultExistedReport['reportNum']
        return existedReportNum

    def fetchStudentHelper(self):
        sql = """select student.StudentID, student.Email, concat(student.FirstName," ",student.LastName) as name, student.DepartmentCode from student
                    inner join user on student.Email=user.Email where user.Role='Student' and user.Status='Active'"""
        cur.execute(sql)
        dbResult = cur.fetchall()
        return dbResult
    # def fetchReportStudentSearch(self, student_id, studentName):
    #     sql = f"""select student.StudentID,student.Email, student.DepartmentCode, concat(student.FirstName," ",student.LastName) as name,
    #           sixmr.ReportID, sixmr.ReportPeriodEndDate, sixmr.B_ReportOrder
    #             from student left join sixmr on sixmr.StudentID=student.StudentID
    #                  where student.StudentID = %s or name
    #              """

    #     cur.execute(sql)
    #     reports = cur.fetchall()
    #     return reports

    def fetchReportFullList(self):
        sql = """select student.StudentID,student.Email, student.DepartmentCode, concat(student.FirstName," ",student.LastName) as name,
              sixmr.ReportID, sixmr.ReportPeriodEndDate,sixmr.Status, sixmr.B_ReportOrder 
                from student left join sixmr on sixmr.StudentID=student.StudentID 
                 inner join user on student.Email=user.Email where user.Role='Student' and user.Status='Active'            
                 """
        cur.execute(sql)
        reports = cur.fetchall()
        return reports

    def fetchReportStatus(self, report_id):
        sql = """select submissionhistory.SubmissionID, submissionhistory.SubmitterEmail, submissionhistory.SubmitterRole, submissionhistory.Date,  submissionhistory.Time 
                 from submissionhistory where ReportID=%s order by submissionhistory.Time"""
        cur.execute(sql, (report_id,))
        results = cur.fetchall()
        
        return results

    def fetchReportID(self):
        sql = """select sixmr.ReportID from sixmr"""
        cur.execute(sql)
        reportId = cur.fetchall()
        return reportId

    def fetchStudent(self, report_id):
        sql = """select sixmr.StudentID, student.Email, concat(student.FirstName," ",student.LastName) as name from sixmr 
        inner join student on sixmr.StudentID = student.StudentID 
        where ReportID=%s"""
        cur.execute(sql, (report_id,))
        student = cur.fetchone()
        return student

    def fetchSubmittedTime(self, report_id, role):
        sql = """select submissionhistory.Date,submissionhistory.Time from submissionhistory
               where ReportID=%s and SubmitterRole=%s """
        cur.execute(sql, (report_id, role))
        submittedTime = cur.fetchall()
        return submittedTime

    def fetchSubmittedReportId(self):
        sql = """select submissionhistory.ReportID from submissionhistory"""
        cur.execute(sql)
        result = cur.fetchall()
        submittedReportId = []
        for data in result:
            submittedReportId.append(data['ReportID'])
        return submittedReportId

    def fetchEmailList(self, report_id):
        sql = """select submissionhistory.SubmitterEmail from submissionhistory
                    where submissionhistory.ReportID=%s"""
        cur.execute(sql, (report_id,))
        result = cur.fetchall()
        emailList = []
        for data in result:
            emailList.append(data['SubmitterEmail'])
        return emailList
    def fetchSixmrStatus(self, report_id):
        sql = """select sixmr.Status from sixmr where ReportID=%s"""
        cur.execute(sql,(report_id,))
        dbResult = cur.fetchone()
        sixmrStatus = dbResult['Status']
        return sixmrStatus
    def fetchReportFinalRole(self, student_id):
        sqlSup = """select supervision.SupervisorID from supervision where supervision.StudentID=%s """
        cur.execute(sqlSup,(student_id,))
        dbSup = cur.fetchall()
        supIdList = []
        for db in dbSup:
            supIdList.append(db['SupervisorID'])
        sqlCon = """select department.ConvenorID from department"""
        cur.execute(sqlCon)
        dbCon = cur.fetchall()
        conIdList = []
        for db in dbCon:
            conIdList.append(db['ConvenorID'])
        finalRole = 'Convenor'
        for supId in supIdList:
            if conIdList.count(supId) > 0:
                finalRole = 'PG Chair'
        return finalRole
    def fetchSupspendedStuId(self):
        sql = """select suspend_record.StudentID from suspend_record"""
        cur.execute(sql)
        dbResult = cur.fetchall()
        suspendedStuId = []
        for db in dbResult:
            suspendedStuId.append(db['StudentID'])
        return suspendedStuId

class PGChair:
    def __init__(self) -> None:
        pass
    def fetchPGChairDetail(self):
        sql = """SELECT concat(staff.FirstName, ' ', staff.LastName) as pgcName, staff.Email FROM staff
            inner join user on user.Email = staff.Email where user.Role='PG Chair';"""   
        cur.execute(sql)
        dbResult = cur.fetchall()
        pgChair = dbResult[0]
        return pgChair
    
    def pgChairList(self):
        sql = """select staff.StaffID, concat(staff.FirstName, ' ', staff.LastName) as 'Staff Name',
                staff.Email,  staff.Phone, staff.DepartmentCode
                from staff
                join user on staff.Email = user.Email
                where user.role = 'PG Chair';"""
        cur.execute(sql)
        pgChairList = cur.fetchall()
        return pgChairList

class Supervisor:
    def __init__(self, studentId=None, email=None):
        self.studentId = studentId
        self.email = email
    def fetchEmailList(self, studentId):
        sql = """select supervision.SupervisorID, supervision.SupervisorType,concat(staff.FirstName,' ', staff.LastName)as supervisorName, staff.Email
                 from supervision inner join staff on supervision.SupervisorID = staff.StaffID
                 where supervision.StudentID = %s"""
        cur.execute(sql, (studentId,))
        result = cur.fetchall()
        emailList = []
        for data in result:
            emailList.append(data['Email'])
        return emailList

    def fetchSupList(self, studentId):
        sql = """select supervision.SupervisorID, supervision.SupervisorType,concat(staff.FirstName,' ', staff.LastName)as supervisorName, staff.Email
                 from supervision inner join staff on supervision.SupervisorID = staff.StaffID
                 where supervision.StudentID = %s"""
        cur.execute(sql, (studentId,))
        supervisors = cur.fetchall()
        return supervisors

    def fetchSupName(self, email):
        sql = """select concat(staff.FirstName,' ', staff.LastName)as supervisorName from staff where staff.Email=%s"""
        cur.execute(sql,(email,))
        dbResult = cur.fetchone()
        supName = dbResult['supervisorName']
        return supName
    
    def supervisorList(self):
        sql = """select staff.StaffID, concat(staff.FirstName, ' ', staff.LastName) as 'Staff Name',
                staff.Email,  staff.Phone, staff.DepartmentCode
                from staff
                join user on staff.Email = user.Email
                where user.role = 'Supervisor';"""
        cur.execute(sql)
        supervisorList = cur.fetchall()
        return supervisorList

class Convenor:
    def __init__(self, studentId=None):
        self.studentId = studentId

    def fetchConvenor(self, studentId):
        sql = """select student.StudentID, concat(staff.FirstName,' ', staff.LastName)as convenorName, staff.Email from student
                inner join department on student.DepartmentCode=department.DepartmentCode
                inner join staff on staff.StaffID = department.ConvenorID
                where student.StudentID=%s"""
        cur.execute(sql, (studentId,))
        convenor = cur.fetchone()
        return convenor

    def convenorList(self):
        sql = """select staff.StaffID, concat(staff.FirstName, ' ', staff.LastName) as 'Staff Name',
                staff.Email,  staff.Phone, staff.DepartmentCode
                from staff
                join user on staff.Email = user.Email
                where user.role = 'Convenor';"""
        cur.execute(sql)
        convenorList = cur.fetchall()
        return convenorList
    
class EmailSenderToMany:
    def __init__(self, email=None, msgContent=None):
        self.email = email
        self.msgContent = msgContent

    def sendEmail(self, email, msgContent):
        current_app.config['MAIL_SERVER'] = "smtp.gmail.com"
        current_app.config['MAIL_PORT'] = 465
        current_app.config['MAIL_USERNAME'] = "system.lupgms.lincoln@gmail.com"
        current_app.config['MAIL_PASSWORD'] = "ibqrfvzclnoksvsm"
        current_app.config['MAIL_USE_TLS'] = False
        current_app.config['MAIL_USE_SSL'] = True
        mail = Mail(current_app)
        recip = email
        msg = Message("Message from Lincoln University Postgraduate Monitoring System", sender="test@lincoln.com", recipients=recip)
        msg.body = msgContent
        mail.send(msg)


class AnalysisReportData:
    def __init__(self, depCode=None, reportPeriod=None, result=None, clauseStr=None, dep=None, criterionId=None, studentId=None, reportId=None, supervisionId=None, assResult=None):
        self.depCode = depCode
        self.reportPeriod = reportPeriod
        self.result = result
        self.clauseStr = clauseStr
        self.criterionId = criterionId
        self.studentId=studentId
        self.supervisionId = supervisionId
        self.reportId = reportId
        self.assResult = assResult
    def fetchStudentNumWithDepCode(self, depcode):
        sql = """select COUNT(*) AS stuNumber from student 
                    inner join user on user.Email = student.Email
                    where user.Role = 'Student' and user.Status = 'Active' 
                    and DepartmentCode=%s"""
        cur.execute(sql, (depcode,))
        result = cur.fetchone()
        number = result['stuNumber']
        return number

    def fetchReportNum(self, depcode, reportPeriod):
        sql = """select COUNT(*) AS repNumber from student 
                inner join sixmr on student.StudentID = sixmr.StudentID 
                where student.DepartmentCode=%s and sixmr.Status = 'Finalised' and sixmr.ReportPeriodEndDate = %s """
        cur.execute(sql, (depcode, reportPeriod))
        result = cur.fetchone()
        number = result['repNumber']
        return number

    def fetchCriterionList(self):
        sql = """select * from evaluationcriterion"""
        cur.execute(sql)
        result = cur.fetchall()
        criterionList = []
        dblength = len(result)
        for index, data in enumerate(result):
            if index != dblength-1:
                criterionList.append(data)
        return criterionList

    def fetchFacultyPerformanceOverAllCurrent(self):
        facultyPerformanceOverAllCurrent = {}
        sqlVeryGood = """select count(c_table.CriterionID) as veryGoodNum  from c_table
         inner join sixmr on sixmr.ReportID = c_table.ReportID
          where  sixmr.ReportPeriodEndDate = '2023-06-30' and c_table.Result='Very Good'"""
        cur.execute(sqlVeryGood)
        resultVeryGood = cur.fetchone()
        veryGoodNum = resultVeryGood['veryGoodNum']

        sqlGood = """select count(c_table.CriterionID) as goodNum  from c_table
         inner join sixmr on sixmr.ReportID = c_table.ReportID
          where  sixmr.ReportPeriodEndDate = '2023-06-30' and c_table.Result='Good'"""
        cur.execute(sqlGood)
        resultGood = cur.fetchone()
        goodNum = resultGood['goodNum']

        sqlSatisfactory = """select count(c_table.CriterionID) as satisfactoryNum  from c_table
         inner join sixmr on sixmr.ReportID = c_table.ReportID
          where  sixmr.ReportPeriodEndDate = '2023-06-30' and c_table.Result='Satisfactory'"""
        cur.execute(sqlSatisfactory)
        resultSatisfactory = cur.fetchone()
        satisfactoryNum = resultSatisfactory['satisfactoryNum']

        sqlUnsatisfactor = """select count(c_table.CriterionID) as unsatisfactorNum  from c_table
         inner join sixmr on sixmr.ReportID = c_table.ReportID
          where  sixmr.ReportPeriodEndDate = '2023-06-30' and c_table.Result='Unsatisfactory'"""
        cur.execute(sqlUnsatisfactor)
        resultUnsatisfactor = cur.fetchone()
        unsatisfactorNum = resultUnsatisfactor['unsatisfactorNum']

        sqlNotRelevant = """select count(c_table.CriterionID) as notRelevantNum  from c_table
         inner join sixmr on sixmr.ReportID = c_table.ReportID
          where  sixmr.ReportPeriodEndDate = '2023-06-30' and c_table.Result='Not Relevant'"""
        cur.execute(sqlNotRelevant)
        resultNotRelevant = cur.fetchone()
        notRelevantNum = resultNotRelevant['notRelevantNum']

        facultyPerformanceOverAllCurrent = {
            'veryGoodNum': veryGoodNum,
            'goodNum': goodNum,
            'satisfactoryNum': satisfactoryNum,
            'unsatisfactorNum': unsatisfactorNum,
            'notRelevantNum': notRelevantNum,
        }
        return facultyPerformanceOverAllCurrent

    def fetchStudentNum(self):
        sql = """select COUNT(*) AS stuNumber from student 
                    inner join user on user.Email = student.Email
                    where user.Role = 'Student' and user.Status = 'Active'
                    """
        cur.execute(sql)
        result = cur.fetchone()
        studentNum = result['stuNumber']
        return studentNum

    def fetchReportNumCurrent(self):
        sql = """select count(*) as reportNumCurrent from sixmr            
          where  sixmr.ReportPeriodEndDate = '2023-06-30' and sixmr.Status  = 'Finalised'"""
        cur.execute(sql)
        result = cur.fetchone()
        reportNumCurrent = result['reportNumCurrent']
        return reportNumCurrent

    def fetchFacultyPerformanceFiltered(self, result, clauseStr):
        sql = f"""select count(c_table.CriterionID) as countedNum  from c_table
         inner join sixmr on sixmr.ReportID = c_table.ReportID
         inner join student on student.StudentID = sixmr.StudentID
          where c_table.Result='{result}' && {clauseStr}"""
        cur.execute(sql)
        result = cur.fetchone()
        countedNum = result['countedNum']
        return countedNum

    # def fetchStudentNumFiltered(self, depCode):
    #     sql = """select count(student.StudentID) as studentNum from student
    #             where student.DepartmentCode = %s"""
    #     cur.execute(sql, (depCode,))
    #     result = cur.fetchone()
    #     studentNum = result['studentNum']
    #     return studentNum
    def countSuspendedStudentWithPeriod(self,depCode,reportPeriod ):
        sql = """SELECT count(suspend_record.StudentID) AS suspendeStuNum FROM suspend_record 
            inner join student on student.StudentID = suspend_record.StudentID 
            where student.DepartmentCode=%s and suspend_record.SuspendPeriod=%s ;"""
        cur.execute(sql,(depCode,reportPeriod))
        dbResult = cur.fetchone()
        suspendeStuNum = dbResult['suspendeStuNum']
        return suspendeStuNum

    def fetchReportNumFiltered(self, reportPeriod, depCode):
        sql = """select count(*) as reportNum from sixmr 
                 inner join student on student.StudentID = sixmr.StudentID
          where  sixmr.ReportPeriodEndDate = %s and student.DepartmentCode = %s  and sixmr.Status  = 'Finalised'"""
        cur.execute(sql, (reportPeriod, depCode))
        result = cur.fetchone()
        reportNum = result['reportNum']
        return reportNum

    def fetchReportNumFilteredPeriod(self, reportPeriod):
        sql = """select count(submissionhistory.ReportID) as reportNum from submissionhistory
                inner join sixmr on sixmr.ReportID = submissionhistory.ReportID
                 inner join student on student.StudentID = sixmr.StudentID
          where  sixmr.ReportPeriodEndDate = %s   and submissionhistory.SubmitterRole = 'Student'"""
        cur.execute(sql, (reportPeriod,))
        result = cur.fetchone()
        reportNum = result['reportNum']
        return reportNum

    def fetchFacultyPerformanceOverPeriod(self, reportPeriod, result):
        sql = """select count(c_table.CriterionID) as countedNum  from c_table
         inner join sixmr on sixmr.ReportID = c_table.ReportID
          where  sixmr.ReportPeriodEndDate = %s and c_table.Result=%s"""
        cur.execute(sql, (reportPeriod, result))
        dbResult = cur.fetchone()
        countedNum = dbResult['countedNum']
        return countedNum

    def fetchCriterion(self, criterionId):
        sql = """SELECT * FROM evaluationcriterion where CriterionID=%s"""
        cur.execute(sql,(criterionId,))
        dbResult = cur.fetchone()
        criterion = dbResult['Criterion']
        return criterion 
    def fetchStudentList(self):
        sqlStu = """select student.StudentID, student.Email, concat(student.FirstName," ",student.LastName) as name, student.DepartmentCode from student
                    inner join user on student.Email=user.Email where user.Role='Student' and user.Status='Active'"""
        cur.execute(sqlStu)
        dbStu = cur.fetchall()
        return dbStu
    def fetchSupList(self, studentId):
        
        sqlSup = """select supervision.SupervisorType, concat(staff.FirstName,' ', staff.LastName) as SupName 
              from student
              inner join user on student.Email = user.Email
              inner join supervision on student.StudentID = supervision.StudentID
              inner join staff on staff.StaffID = supervision.SupervisorID
              where user.Role = 'Student' and user.Status = 'Active' and student.StudentID= %s;"""
        cur.execute(sqlSup, (studentId,))
        dbSup = cur.fetchall()
        supList = []
        for sup in dbSup:
            supList.append(
               sup['SupName']
            )

        return supList
    def fetchReportRating(self,studentId):
        sql="""select sixmr.ReportPeriodEndDate, sixmr.E_ConvenorRating from sixmr
        where sixmr.StudentID = %s and sixmr.Status = 'Finalised' 
        order by sixmr.ReportPeriodEndDate"""
        cur.execute(sql,(studentId,))
        dbResult = cur.fetchall()
        ratingLsit = []
        
        for db in dbResult:
            ratingLsit.append({
                str(db['ReportPeriodEndDate']): db['E_ConvenorRating'],
            })
        return ratingLsit
    def fetchReportPeriodList(self,studentId):
        sql="""select sixmr.ReportPeriodEndDate, sixmr.E_ConvenorRating from sixmr
        where sixmr.StudentID = %s and sixmr.Status = 'Finalised' 
        order by sixmr.ReportPeriodEndDate"""
        cur.execute(sql,(studentId,))
        dbResult = cur.fetchall()
        periodLsit = []
        for db in dbResult:
            periodLsit.append(
                str(db['ReportPeriodEndDate']),
            )
        return periodLsit
    def checkIfStudentSuspended(self,studentId,reportPeriod):
        sql = """SELECT * FROM suspend_record where suspend_record.StudentID=%s and suspend_record.SuspendPeriod=%s order by suspend_record.SuspendPeriod"""
        cur.execute(sql, (studentId,reportPeriod))
        dbResult = cur.fetchall()
        if len(dbResult) == 0:
            studentIsSuspended = False
        else:
            studentIsSuspended = True
        return studentIsSuspended
    def fetchIndividulReportId(self,studentId,reportPeriod):
        sql = """select sixmr.ReportID from sixmr where sixmr.StudentID=%s and sixmr.ReportPeriodEndDate=%s and sixmr.Status='Finalised'"""
        cur.execute(sql,(studentId,reportPeriod))
        dbResult = cur.fetchone()
        if dbResult:
            reportId = dbResult['ReportID']
        else:
            reportId = None
        return reportId
    def fetchSupervisionIDList(self,studentId):
        sql = """select supervision.SupervisionID from supervision where supervision.StudentID = %s"""
        cur.execute(sql,(studentId,))
        dbResult = cur.fetchall()
        supervisionIDList = []
        for db in dbResult:
            supervisionIDList.append(db['SupervisionID'])
        return supervisionIDList
    def fetchReportResult(self,reportId, supervisionId, assResult):
        sql = """select count(e_table.AssessmentID) as resultNum from e_table
            left join supervisorassessment on supervisorassessment.AssessmentID = e_table.AssessmentID
            where supervisorassessment.ReportID=%s and supervisorassessment.SupervisionID = %s and e_table.Result=%s;"""
        cur.execute(sql,(reportId, supervisionId, assResult))
        dbResult = cur.fetchone()
        resultNum = dbResult['resultNum']
        return resultNum
class SixMRModule:
    def __init__(self, student_id=None, report_id=None, sixmr_instance=None):
        self.student_id = student_id
        self.report_id = report_id
        self.sixmr_instance = SixMR()

    def view_6mr_report(self, student_id, report_id):
        ####### SECTION A ########
        # Get Reporting Period End Date.
        period_ending = self.sixmr_instance.get_period_ending(report_id)['ReportPeriodEndDate']
        # Get student profile for Section A other than scholarship and employment.
        cur.execute("SELECT Email FROM Student WHERE StudentID=%s;", (student_id,))
        email = cur.fetchone()['Email']
        student_profile = self.sixmr_instance.student_profile(email)
        # Get supervision information.
        supervisors = self.sixmr_instance.student_supervisors(student_id)
        # Get current scholarship information.
        scholarships = self.sixmr_instance.student_current_scholarship(student_id)
        # Get current employment information.
        employment = self.sixmr_instance.student_current_employment(student_id)
        ####### SECTION B ########
        # Get B_Table data.
        b_table = self.sixmr_instance.get_b_table(report_id)
        b_options = ['Yes','No']
        # Get B_Approval data.
        b_approval = self.sixmr_instance.get_b_approval(report_id)
        approval_options = ['Needed','Approval Given','Not Needed']
        # Get Report Order data
        report_order = self.sixmr_instance.get_6mr_report_order(report_id)
        report_order_table = self.sixmr_instance.get_report_order_table()
        ####### SECTION C ########
        # Get C_Table data
        c_table = self.sixmr_instance.get_c_table(report_id)
        rating_options = ['Very Good', 'Good', 'Satisfactory', 'Unsatisfactory', 'Not Relevant']
        # Get C_Meeting Frequency data. 
        frequency = self.sixmr_instance.get_meeting_frequency(report_id)
        fqc_options = ['Weekly', 'Fortnightly', 'Monthly', 'Every 3 months', 'Half yearly', 'Not at all']
        # C_Feedback period.
        feedback_period = self.sixmr_instance.get_feedback_period(report_id)
        fb_options = ['1 week','2 weeks','1 month','3 months']
        # C_Feedback channel.
        c_feedback_channel_data = self.sixmr_instance.get_c_feedback_channel_table(report_id)
        ####### SECTION D ########
        # D1 table.
        d1_data = self.sixmr_instance.get_d1_data(report_id)
        status_options = ['Completed', 'Incomplete','Select One']
        d1_objective_change = self.sixmr_instance.get_d1_objective_change(report_id)
        # D2 data.
        d2_data = self.sixmr_instance.get_6mr_data(report_id)['D2_CovidEffects']
        # D3 data.
        d3_data = self.sixmr_instance.get_6mr_data(report_id)['D3_AcademicAchievements']
        # D4 data.
        d4_data = self.sixmr_instance.get_d4_data(report_id)
        # D5 data.
        d5_data = self.sixmr_instance.get_d5_data(report_id)
        # D5 total expenditure
        d5_expenditure = self.sixmr_instance.get_d5_expenditure(report_id)
        # D5 comments
        d5_comments = self.sixmr_instance.get_6mr_data(report_id)['D5_Comments']
        ####### SECTION E ########
        # Check if at least 1 supervisor has finished a section E part of the report.
        # and get the assessmentIDs, Completion Date, supervisor names and supervisor types for the finished section E parts.
        sql = """SELECT sa.AssessmentID, sa.CompletionDate, sa.CompletionTime, CONCAT(stf.FirstName,' ',stf.LastName) AS SupervisorName, sup.SupervisorType
                FROM SupervisorAssessment AS sa
                JOIN Supervision AS sup
                ON sa.SupervisionID=sup.SupervisionID
                JOIN Staff AS stf ON sup.SupervisorID=stf.StaffID
                WHERE sa.ReportID=%s AND sa.CompletionDate IS NOT NULL;"""
        cur.execute(sql, (report_id,))
        e_assessment_info = cur.fetchall()
        # If no section E has been completed.
        if e_assessment_info == False:
            e_assessment_content = None
        else:
        # If at least 1 section E has been completed, get section E content
            assessment_ids = []
            for row in e_assessment_info:
                assessment_ids.append(row['AssessmentID'])
            e_assessment_content = []
            for assessment_id in assessment_ids:
                # Get section E data.
                # 1.Get E_Table data
                cur.execute("""SELECT e.CriterionID,ac.Criterion,e.Result FROM E_Table AS e JOIN AssessmentCriterion AS ac ON e.CriterionID=ac.CriterionID WHERE e.AssessmentID=%s;""", (assessment_id,))
                e_table = cur.fetchall()
                # 2.Get the rest of the Section E data.
                cur.execute("""SELECT E_Comments, E_IfRecomCarriedOut FROM SupervisorAssessment WHERE AssessmentID=%s;""",(assessment_id,))
                e_rest = cur.fetchone()
                # pack all the e_assessment_info and e_table data into a list of dictionaries.
                index = assessment_ids.index(assessment_id)
                e_assessment_content.append({'e_assessment_info':e_assessment_info[index],'e_table':e_table,'e_rest':e_rest})
        e_rating_options = ['Excellent', 'Good', 'Satisfactory', 'Below Average', 'Unsatisfactory']
        e_irco_options = ['Yes', 'No', 'N/A']
        # Section E Convenor/PG Chair part
        # Get the section E convenor/PG Chair assessment content.
        cur.execute("""SELECT * FROM SixMR WHERE ReportID=%s AND Status='Finalised';""",(report_id,))
        final_assessment = cur.fetchone()
        # If the report has been finalised.
        if final_assessment:
            #Get the convenor/pg chair's name,role,FinalisedDate.
            cur.execute("""SELECT CONCAT(stf.FirstName,' ',stf.LastName) AS FinaliserName, six.FinaliserRole, six.FinalisedDate, six.FinalisedTime FROM SixMR AS six JOIN Staff AS stf ON stf.StaffID=six.FinaliserID WHERE six.ReportID=%s;""",(report_id,))
            finaliser_info = cur.fetchone()
            is_finalised = True
        else:
            finaliser_info = None
            is_finalised = False
        ####### SECTION F ########
        # See if section F is included.
        if_section_f = self.sixmr_instance.if_section_f(report_id)
        if if_section_f == 'Yes':
            # Get F_Table data.
            f_table = self.sixmr_instance.get_f_table(report_id)
            # Check if pg chair has resonded to the section f
            cur.execute("""SELECT * FROM F WHERE ReportID=%s AND HasResponded=1;""",(report_id,))
            pgChair_response=cur.fetchone()
            if pgChair_response==None:
                pgChair_response = False
        else:
            f_table = False
            pgChair_response = False
        
        return render_template('viewReport.html',period_ending=period_ending,
        student_profile=student_profile,supervisors=supervisors,scholarships=scholarships,
        employment=employment,b_table=b_table,b_options=b_options,b_approval=b_approval,
        approval_options=approval_options,report_order=report_order,report_order_table=report_order_table,
        c_table=c_table,rating_options=rating_options,frequency=frequency,fqc_options=fqc_options,
        feedback_period=feedback_period,fb_options=fb_options,c_feedback_channel_data=c_feedback_channel_data,
        d1_data=d1_data,status_options=status_options,d1_objective_change=d1_objective_change,
        d2_data=d2_data,d3_data=d3_data,d4_data=d4_data,d5_data=d5_data,d5_comments=d5_comments,
        d5_expenditure=d5_expenditure,f_table=f_table,student_id=student_id,report_id=report_id,
        e_assessment_content=e_assessment_content,e_rating_options=e_rating_options,e_irco_options=e_irco_options,
        finaliser_info=finaliser_info,final_assessment=final_assessment,pgChair_response=pgChair_response,
        is_finalised=is_finalised)