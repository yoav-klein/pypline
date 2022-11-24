
# Pypline - Python packages for pipelines
---

This Python distribution package contains some packages for use in CI/CD pipelines.

This dist package is intended to be extensible - whenever you see a need for a new package 
to be used in CI/CD pipelines, create a new package in this repository.


## Packages
---
### build_mail
This package is used to send a summary mail after a CI/CD build.

The mail contains some basic information about the build - build name, build number, result, time, etc.
Additionally, depending on the tools used during the build, the mail contains some additional information.
For example, if SonarQube is used, the user can have the mail contain results of the scan, etc. 

After installing the `pypline` dist package, you can just run:
```
$ send-mail <arguments>
```

Arguments:
...