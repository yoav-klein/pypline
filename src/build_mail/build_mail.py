
import os
import argparse

from jinja2 import Environment, PackageLoader

class Globals:
    ci_env = ''


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

def sonarqube():
    # contruct html block with results
    html_block = "sonarqube results"
    return html_block

def test_results():
    html_block = "test results"
    return html_block

def basic() -> dict:
    """
    returns a dictionary that contains basic build information
    """

    # project_name - TFS - Team Project, Jenkins - none
    # repo_name
    # branch
    # commit ID/Commit URL
    # build number/id
    # trigger
    # status

    if(Globals.ci_env == "TFS"):
        data = {
            'project_name': os.environ['SYSTEM_TEAMPROJECT'],
            'repo_name': os.environ['BUILD_REPOSITORY_NAME'],
            'branch_name': os.environ['BUILD_SOURCEBRANCHNAME'],
            'commit_title': os.environ['BUILD_SOURCEVERSIONMESSAGE'],
            'commit_id': os.environ['BUILD_SOURCEVERSION'],
            'build_url': f"{os.environ['SYSTEM_TEAMFOUNDATIONCOLLECTIONURI']}/Amitay_Test_Proj/_build/results?buildId=11373"
        }

            #build_num = os.environ['BUILD_ID']
            #message_v = f"[{os.environ['SYSTEM'].upper()} {os.environ['AGENT_JOBSTATUS']}] {os.environ['BUILD_DEFINITIONNAME']} - {os.environ['BUILD_REPOSITORY_NAME']}:{os.environ['BUILD_SOURCEBRANCHNAME']}"
    elif(Globals.ci_env == "Jenkins"):
        project_name = "MYPROJECT"
        repo_name = "repo"
        branch_name = "master"
        commit_title = "bla bla"
        commit_id = "12345678"
        build_url = "nothing" 
        build_num = "12345678"
        message_v = "mail message"

    data = {
        "build_name": "Kuku",
        "build_number": 100,
        "result": "Success",
        "commit_id": "1a2b3c",
        "branch": "develop",
        "repository": "Kipat Barzel"
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

    print(context)
    print(template.render(context))


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
    pass

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