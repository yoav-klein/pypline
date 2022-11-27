import re
import glob
import os
import json
import argparse
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import sys
import subprocess
import urllib.parse


#################################################################################

parser=argparse.ArgumentParser()

parser.add_argument("-KWP", "--kwProject",help="Klocwork Project Name",nargs='+')
parser.add_argument("-SQP", "--SqProject",help="Sonarqube Project Name",nargs='+')
parser.add_argument("-MREC", "--mail_recipants",help="List of mail addresses separated with space.",nargs='+')
parser.add_argument("-CCOV", "--Code_Coverage",help="Path To index.html file.")

args=parser.parse_args()
#################################################################################

add_table_bool= False
KwToken =""
table_rows = ""
ProjectName = ""
BuildId = ""

############################# Enviroment Variables ##############################
env_type = "test"

if(env_type == "TFS"):
	Project_Name = os.environ['SYSTEM_TEAMPROJECT']
	repo_name = os.environ['BUILD_REPOSITORY_NAME']
	branch_name = os.environ['BUILD_SOURCEBRANCHNAME']
	commit_Title = os.environ['BUILD_SOURCEVERSIONMESSAGE']
	commit_id = os.environ['BUILD_SOURCEVERSION']
	build_url = f"{os.environ['SYSTEM_TEAMFOUNDATIONCOLLECTIONURI']}/Amitay_Test_Proj/_build/results?buildId=11373" 
	build_num = os.environ['BUILD_ID']
	message_v = f"[{os.environ['SYSTEM'].upper()} {os.environ['AGENT_JOBSTATUS']}] {os.environ['BUILD_DEFINITIONNAME']} - {os.environ['BUILD_REPOSITORY_NAME']}:{os.environ['BUILD_SOURCEBRANCHNAME']} "

elif(env_type == "test"):
	Project_Name = "MYPROJECT"
	repo_name = "repo"
	branch_name = "master"
	commit_Title = "bla bla"
	commit_id = "12345678"
	build_url = "nothing" 
	build_num = "12345678"
	message_v = "mail message"
	

################################ KW FUNCTIONS ###################################

def GetToken() :
    ltoken_file = glob.glob(f"{os.environ['USERPROFILE']}\\.klocwork\\ltoken")

    with open(''.join(ltoken_file)) as f:
        tokenn = (re.search(f"{os.environ['USERNAME'].upper()}.*;(.*)",f.read()))

    return tokenn[1]

def KW_Query_Resp(status, state, severity) :
    Body = f"action=report&user={os.environ['USERNAME']}&project={ProjectName}&build={BuildId}&ltoken={KwToken}&filterQuery="
    uri = "http://<kw_server>:8080/review/api"

    if status:
        Body+=f"status:{status} "
    if state:
        Body+=f"state:{state} "
    if severity:
        Body+=f"severity:{severity}"

    json_res = subprocess.run(f'curl --data "{Body}" {uri}', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    
    s = json.loads(json_res.stdout)
    
    return s['data'][0][0] 


def KW_Query_Url(status, state, severity) :

    url_queries = ""

    if status:
        status_query="status:"
        s1 = status.split(',')
        for st in s1:
            status_query+=f"+{st},"
        status_query = urllib.parse.quote(urllib.parse.quote(status_query.removesuffix(",")))
        url_queries += status_query
    if state:
        state_query="state:"
        s1 = state.split(',')
        for st in s1:
            state_query+=f"+{st},"
        state_query = urllib.parse.quote(urllib.parse.quote(state_query.removesuffix(",")))
        url_queries += f"+{state_query}"
    if severity:
        severity_query = urllib.parse.quote(urllib.parse.quote(f"severity:{severity}"))
        url_queries += f"+{severity_query}"

    return f"http://<kw_server>:8080/review/insight-review.html#issuelist_goto:project={ProjectName},searchquery=build%253A{BuildId}+{url_queries},sortcolumn=id,sortdirection=ASC,start=0,view_id=1"  

def KW_Get_Last_Build_ID(KW_proj) :

    uri = "http://<kw_server>:8080/review/api"
    Body = f"action=builds&user={os.environ['USERNAME']}&project={KW_proj}&ltoken={KwToken}"

    json_res = subprocess.run(f'curl --data "{Body}" {uri}', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return json.loads(json_res.stdout.decode('utf-8').splitlines()[0])['name']
############################## SonarQube FUNCTIONS ##############################

if args.SqProject:
    add_table_bool = True
    
    for SQProjectName in args.SqProject:
        
        add_table_bool = True


        SQToken = "<token>"
        sq_proj = SQProjectName
        uri = f"https://<SQ_server>/api/issues/search?componentKeys={sq_proj}&resolved=false"



        def get_issues_by_severity(severity,issue_type=''):
            if(issue_type):
                issue_type = "&types="+issue_type

            json_res = subprocess.run(f'curl -u {SQToken}: {uri}&severities={severity}{issue_type}', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            s = json.loads(json_res.stdout)
            
            return s["total"]

        
        table_rows+=f"""\
                <tr>
                    <td> SonarQube.</td>
                    <td>  </td>
                    <td>
                        <table >
                        <tr>
                            <th style='background-color: blue;'>Status</th>
                            <th style='background-color: blue;'>Critical</th>
                            <th style='background-color: blue;'>Major </th>
                            <th style='background-color: blue;'>Blocker</th>
                            <th style='background-color: blue;'>Minor</th>
                        </tr>
                        <tr>
                            <td> Bugs.</td>
                            <td>{get_issues_by_severity('CRITICAL','BUG')}</td>
                            <td>{get_issues_by_severity('MAJOR','BUG')}</td>
                            <td>{get_issues_by_severity('BLOCKER','BUG')}</td>
                            <td>{get_issues_by_severity('MINOR','BUG')}</td>
                        </tr>
                        <tr>
                            <td> Vulnerabilities.</td>
                            <td>{get_issues_by_severity('CRITICAL','VULNERABILITY')}</td>
                            <td>{get_issues_by_severity('MAJOR','VULNERABILITY')}</td>
                            <td>{get_issues_by_severity('BLOCKER','VULNERABILITY')}</td>
                            <td>{get_issues_by_severity('MINOR','VULNERABILITY')}</td>
                        </tr>
                        <tr>
                            <td> Code Smells.</td>
                            <td>{get_issues_by_severity('CRITICAL','CODE_SMELL')}</td>
                            <td>{get_issues_by_severity('MAJOR','CODE_SMELL')}</td>
                            <td>{get_issues_by_severity('BLOCKER','CODE_SMELL')}</td>
                            <td>{get_issues_by_severity('MINOR','CODE_SMELL')}</td>
                        </tr>
                        </table><br>
                        Project: {sq_proj} <br>
                    </td>
                </tr>
                """







#################################################################################




if args.kwProject:
    add_table_bool = True
    
    print("set kw-project to %s" % args.kwProject)

    KwToken = GetToken()

    
    
    for ProjectName in args.kwProject:

        BuildId = KW_Get_Last_Build_ID(ProjectName)    
        
        table_rows+=f"""\
        <tr>
            <td> KlockWork.</td>
            <td> <a href='{KW_Query_Url("","","")}'>Build<a> </td>
            <td>
                <table >
                <tr>
                    <th style='background-color: blue;'>Status</th>
                    <th style='background-color: blue;' >Critical</th>
                    <th style='background-color: blue;'>Error </th>
                    <th style='background-color: blue;'>Warning</th>
                    <th style='background-color: blue;'>Review</th>
                </tr>
                <tr>
                    <td><a href='{KW_Query_Url("","New","")}'> {KW_Query_Resp("","New","")} New Issues.</a></td>
                    <td><a href='{KW_Query_Url("","New","1")}'> {KW_Query_Resp("","New","1")}</a></td>
                    <td><a href='{KW_Query_Url("","New","2")}'> {KW_Query_Resp("","New","2")}</a></td>
                    <td><a href='{KW_Query_Url("","New","3")}'> {KW_Query_Resp("","New","3")}</a></td>
                    <td><a href='{KW_Query_Url("","New","4")}'> {KW_Query_Resp("","New","4")}</a></td>
                </tr>
                <tr>
                    <td><a href='{KW_Query_Url("Analyze,Fix","","")}'> {KW_Query_Resp("Analyze,Fix","","")} Open Issues</a></td>
                    <td><a href='{KW_Query_Url("Analyze,Fix","","1")}'> {KW_Query_Resp("Analyze,Fix","","1")}</a></td>
                    <td><a href='{KW_Query_Url("Analyze,Fix","","2")}'> {KW_Query_Resp("Analyze,Fix","","2")}</a></td>
                    <td><a href='{KW_Query_Url("Analyze,Fix","","3")}'> {KW_Query_Resp("Analyze,Fix","","3")}</a></td>
                    <td><a href='{KW_Query_Url("Analyze,Fix","","4")}'> {KW_Query_Resp("Analyze,Fix","","4")}</a></td>
                </tr>
                </table><br>
                Project: {ProjectName} <br>
                BuildId: {BuildId} <br>
            </td>
        </tr>
        """


if args.Code_Coverage:
    add_table_bool = True
    text_file = glob.glob(args.Code_Coverage)
    print(''.join(text_file))
    with open(''.join(text_file)) as f:
        x = (re.search('cover.* (\d+) lines.*(\d+)%.*uncover.* (\d+).* lines \((\d+)%\)',f.read()))

    coverage_summery=f"Total line : {int(x.group(1)) + int(x.group(3))} ,  Lines covered : {x.group(1)} ({x.group(2)}%)"

    table_rows+=f"""\
    <tr>
        <td> Code Coverage</td>
        <td> None </td>
        <td>{coverage_summery} </td>
    </tr>
    """

table_content = ""
if add_table_bool:
    table_content=f"""\
    <table >
        <tr>
            <th>Tools</th>
            <th>Links</th>
            <th>Short summary </th>
        </tr>
        {table_rows}
    </table> 
    """


smtpserver="mw.<server>"
sender=f"{os.environ['USERNAME']}@<server>"

send_to = "amitayn@<server>"

if args.mail_recipants:
    for name in args.mail_recipants:
        send_to+=f",{name}@<server>"

print(send_to)

message=MIMEMultipart("alternative")
message["Subject"]= message_v
message["From"]=sender
message["To"]=send_to

text="""\
this is an example of content to email message
"""

html=f"""\
<html>
<style>
    table,th,td {{border: 1px solid black; border-collapse: collapse; }}
    th, td{{padding: 5px;}}
    th{{font-size: 20px; background-color: #FFD966;}}
</style>
    <strong style="font-size: 25px;"><u>General Summary:</u></strong><br>
    <strong>Project Name :</strong>{Project_Name}<br>
    <strong> Repo:  </strong> {repo_name} <br>
    <strong> Branch:  </strong> {branch_name} <br>
    <strong> Commit Title:  </strong> {commit_Title} <br>
    <strong>Commit id:  </strong> {commit_id} <br>
    <strong>Build ID:  </strong> <a href="build_url"> {build_num} </a><br>
    <strong> date:  </strong> <font color="green">{datetime.now().strftime("%d/%m/%Y  %H:%M:%S")} </font><br>
    
    <br>{table_content}
<html>
"""

#part1=MIMEText(text,"plain")
part2=MIMEText(html,"html")

#message.attach(part1)
message.attach(part2)

server=smtplib.SMTP(smtpserver,25)
server.ehlo()
server.starttls()
server.sendmail(sender,send_to.split(","),message.as_string())
server.quit()
