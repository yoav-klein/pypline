
from jinja2 import Environment, PackageLoader

def blackduck() -> str:
    """
    return html block 
    """
    ...
    # constuct html block with bd results
    html_block = "..."
    return html_block

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

    data = {
        "build_name": "Kuku",
        "build_number": 100,
        "result": "Success",
        "commit_id": "1a2b3c",
        "branch": "develop",
        "repository": "Kipat Barzel"
    }
    return data

def render_template():
    environment = Environment(loader=PackageLoader("build_mail"))
    template = environment.get_template("mail.html")
    
    context = {
        "title": "Build summary",
        "basic": basic(),
        "sonarqube": sonarqube(),
        "test_results": test_results()
    }
    print(template.render(context))


def main():
    render_template()


if __name__ == "__main__":
    main()


## TODO:
#
#   - receive parameters with argparse
#   - decide what needs to be in the basic build info 
#   - read build info from evnironment - depends on Azure DevOps/Jenkins
#   - create a package that can be installe with pip install
#   - style the HTML document better
#   - 
#