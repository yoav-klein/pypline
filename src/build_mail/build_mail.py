
import os
import re 
import argparse
import subprocess
import json
from jinja2 import Environment, PackageLoader
import xml.etree.ElementTree as ET

class Globals:
    ci_env = ''

def coverage(coberture_path) -> dict:

    root = ET.parse(coberture_path).getroot()

    dic_of_atrib = root.attrib
    dic_of_atrib['line-rate'] = "{0:.1%}".format(float(dic_of_atrib['line-rate']))
    dic_of_atrib["uncovered-lines"] = int(dic_of_atrib["lines-valid"]) - int(dic_of_atrib["lines-covered"])
    for atr_k in dic_of_atrib :
        print(f"{atr_k}: {dic_of_atrib[atr_k]}")
    return dic_of_atrib

def trivy(report_path) -> str:

    f = open(report_path, "r")

    html_content = f.read()

    m=re.match('.*</head>.*<body>(.*)</body>.*', html_content , flags=re.S)
    body_contnet = m.group(1)

    f.close()

    return body_contnet
    
def blackduck() -> str:
    """
    return html block 
    """
    ...
    # constuct html block with bd results
    html_block = "..."
    return html_block

def klocwork(kw_project: str, kw_server: str) -> dict:
    print("==== KLOCWORK =====")
    print(kw_project)
    print(kw_server)

    return {
        'issue1': "not goood",
        'issue2': "very good"
    }

def sonarqube(sonar_project, sonar_token,sonar_server="sonarqube.rafael.co.il"):
    # contruct html block with results

    sonar_server="sonarqube.rafael.co.il"

    uri = f"https://{sonar_server}/api/issues/search?componentKeys={sonar_project}&resolved=false"

    def get_issues_by_severity(severity,issue_type=''):
        if(issue_type):
            issue_type = "&types="+issue_type

        json_res = subprocess.run(f'curl -u {sonar_token}: {uri}&severities={severity}{issue_type}', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        res = json.loads(json_res.stdout)

        return res["total"] 

    sq_dic ={
        'BUG':{},
        'VULNERABILITY':{},
        'CODE_SMELL':{}
    }
    
    sq_dic['project_name'] = sonar_project

    for type in ('BUG','VULNERABILITY','CODE_SMELL'):
        for severity in('CRITICAL','MAJOR','BLOCKER','MINOR'):
            sq_dic[type][severity] = get_issues_by_severity(severity,type)
 

    return sq_dic

def test_results():
    html_block = "test results"
    return html_block


def basic() -> dict:
    """
    returns a dictionary that contains basic build information
    """
    # Mail subject : Pipeline Name - Project Name - Build Status
    
    # project name    | TFS - body
    # pipeline name   | TFS/Jenkins - subject, body
    # build number    | TFS/Jenkins - body (link to build_url)
    # status          | TFS/Jenkins - subject, body
    # trigger         | TFS - body
    
    # repo name       | TFS - subject, body
    # branch          | TFS/Jenkins - subject, body
    # commit id       | TFS/Jenkins - 8 chars in subject, body (NTH: link to the commit in the repo)
    # commit msg      | TFS - body
    
    # subject_tfs    : pipeline_name, status, repo_name, branch, commit ID - f'[Build {status}] - {pipeline_name} - {repo_name}:{branch} - {commit_id}'
    # subject_jenkins: pipeline_name, status, branch, commit_id - f'[Build {status}] - {pipeline_name} - {*maybe repo name:branch} - {commit_id}'

    if(Globals.ci_env == "TFS"):
        data = {
            'project_name': { 'name': 'Project Name', 'val': os.environ['SYSTEM_TEAMPROJECT'] },
            'pipeline_name': { 'name': 'Pipeline Name', 'val': os.environ['BUILD_DEFINITIONANME'] },
            'build_number': { 'name': 'Build number', 'val':  os.environ['BUILD_BUILDID'], 
                'link': f"{os.environ['SYSTEM_COLLECTIONURI']}/{os.environ['SYSTEM_TEAMPROJECT']}/build/results?buildId={os.environ['BUILD_BUILDID']}"},
            'status': { 'name': 'Status', 'val': os.environ['AGENT_JOBSTATUS'] },
            'trigger': { 'name': 'Trigger', 'val': os.environ['BUILD_REASON']},
            'repo_name': { 'name': 'Repository Name', 'val': os.environ['BUILD_REPOSITORY_NAME'] },
            'branch_name': { 'name': 'Branch', 'val': os.environ['BUILD_SOURCEBRANCHNAME'] },
            'commit_message': { 'name': 'Commit Message', 'val': os.environ['BUILD_SOURCEVERSIONMESSAGE'] }, # NTH: link to the commit
            'commit_id': { 'name': 'Commit ID', 'val':os.environ['BUILD_SOURCEVERSION'] }
        }
        
    elif Globals.ci_env == "Jenkins":
        data = {
            'pipeline_name': { 'name': 'Pipeline Name', 'val': os.environ['JOB_NAME'] },
            'build_number': { 'name': 'Build number', 'val':  os.environ['BUILD_ID'],  'link': os.environ['BUILD_URL'] },
            'status': { 'name': 'Status', 'val': os.environ['AGENT_JOBSTATUS'] },
            'branch_name': { 'name': 'Branch', 'val': os.environ['GIT_BRANCH'] },
            'commit_id': { 'name': 'Commit ID', 'val':os.environ['GIT_COMMIT'] }
        }
    
    elif Globals.ci_env == "test":
        data = {
            'project_name': { 'name': 'Project Name', 'val': "DemoProject" },
            'pipeline_name': { 'name': 'Pipeline Name', 'val': "Demo Pipeline" },
            'build_number': { 'name': 'Build number', 'val':  "12", 
                'link': "http://broken.url"},
            'status': { 'name': 'Status', 'val': "Success" },
            'trigger': { 'name': 'Trigger', 'val': "Manual" },
            'repo_name': { 'name': 'Repository Name', 'val': "KipatBarzel" },
            'branch_name': { 'name': 'Branch', 'val': "feature" },
            'commit_message': { 'name': 'Commit Message', 'val': "one two three" }, # NTH: link to the commit
            'commit_id': { 'name': 'Commit ID', 'val': "a12b34c56" }
         }

    return data

def render_template(args):
    environment = Environment(loader=PackageLoader("build_mail"))
    template = environment.get_template("mail.html")
    
    context = {
        "title": "Build summary",
        "basic": basic()
    }

    if args.sonar_project:
        context['sonarqube'] = sonarqube(args.sonar_project, args.sonar_token, args.sonar_server)
    
    if args.kw_project:
        context['klocwork'] = klocwork(args.kw_project, args.kw_server)

    if args.code_coverage:
        context['coverage'] = coverage(args.code_coverage)
    if args.trivy_report_html:
        context['trivy'] = trivy(args.trivy_report_html)

    print(context)
    print(template.render(context))
    f = open("report.html", "w")
    f.write(template.render(context))
    f.close()


def parse_args():
    parser = argparse.ArgumentParser(description="Send build summary mail")

    parser.add_argument("--kw-server", help="Klocwork server URL, if not specified - default server will be used")
    parser.add_argument("--kw-project", help="Klocwork Project Name")
    parser.add_argument("--sonar-project", help="Sonarqube Project Name")
    parser.add_argument("--sonar-token", help="Token for SonarQube project") # needs to pass: token
    parser.add_argument("--sonar-server", help="SonarQube server, if not specified - default server will be used")
    parser.add_argument("--mail-recipients", help="List of email addresses", nargs='+')
    parser.add_argument("--code-coverage", help="Path To cobertura-formatted code coverage XML file")
    parser.add_argument("--unittest-report", help="Path to Junit-formatted test report XML file")
    parser.add_argument("--trivy-report-html", help="Path to Trivy scan report HTML file")

    args = parser.parse_args()
    if args.sonar_project and not args.sonar_token:
        parser.error("Must specify --sonar-token along with --sonar-project")
    return args

def set_environment():
    if 'JENKINS_HOME' in os.environ:
        Globals.ci_env = "Jenkins"
    if 'SYSTEM_COLLECTIONURI' in os.environ:
        Globals.ci_env = "TFS"
    else:
        Globals.ci_env = "test"


def main():
    args = parse_args()
    print(args)
    set_environment()
    render_template(args)


if __name__ == "__main__":
    main()


## Milestones:
# 1. Mail with basic information - working in both Jenkins and Azure DevOps
#
# Tasks:
#  - decide what needs to be in the basic build info
#  - style the HTML document better
#  - implement


## TODO:
#
#   1. 
#
#   - 

#   - read build info from evnironment - depends on Azure DevOps/Jenkins
#
