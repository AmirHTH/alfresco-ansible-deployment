"""Repo Tests"""
import os
import pytest
from hamcrest import assert_that, contains_string

# pylint: disable=redefined-outer-name
@pytest.fixture()
def get_ansible_vars(host):
    """Define get_ansible_vars"""
    repository_role = "file=../../vars/main.yml name=repository_role"
    tomcat_role = "file=../../../roles/tomcat/vars/main.yml name=tomcat_role"
    java_role = "file=../../../roles/java/vars/main.yml name=java_role"
    common_vars = "../../../common/vars/main.yml name=common_vars"
    common_defaults = "../../../common/defaults/main.yml name=common_defaults"
    group_vars = "../../../../group_vars/all.yml name=group_vars"
    ansible_vars = host.ansible("include_vars", tomcat_role)["ansible_facts"]["tomcat_role"]
    ansible_vars.update(host.ansible("include_vars", repository_role)["ansible_facts"]["repository_role"])
    ansible_vars.update(host.ansible("include_vars", java_role)["ansible_facts"]["java_role"])
    ansible_vars.update(host.ansible("include_vars", common_vars)["ansible_facts"]["common_vars"])
    ansible_vars.update(host.ansible("include_vars", group_vars)["ansible_facts"]["group_vars"])
    ansible_vars.update(host.ansible("include_vars", common_defaults)["ansible_facts"]["common_defaults"])
    return ansible_vars

test_host = os.environ.get('TEST_HOST')

def test_repo_service_is_running_and_enabled(host, get_ansible_vars):
    """Check repository service"""
    repository = host.service("alfresco-content.service")
    assert_that(repository.is_running)
    assert_that(repository.is_enabled)

def test_alfresco_log_exists(host, get_ansible_vars):
    "Check that alfresco.log exists in /var/log/alfresco"
    assert_that(host.file("/var/log/alfresco/alfresco.log").exists)

def test_alfresco_context_200(host, get_ansible_vars):
    "Check that /alfresco context is available and returns a HTTP 200 status code"
    cmd = host.run("curl -iL --user admin:admin --connect-timeout 5 http://{}:8080/alfresco".format(test_host))
    assert_that(cmd.stdout, contains_string("Welcome to Alfresco"), test_host)
    assert_that(cmd.stdout, contains_string("HTTP/1.1 200"))

def test_alfresco_api(host, get_ansible_vars):
    "Check the repository is installed correctly by calling the discovery API (/alfresco/api/discovery)"
    cmd = host.run("curl -iL --user admin:admin --connect-timeout 5 http://{}:8080/alfresco/api/discovery".format(test_host))
    assert_that(cmd.stdout, contains_string(get_ansible_vars["acs"]["version"]))

def test_share_log_exists(host, get_ansible_vars):
    "Check that share.log exists in /var/log/alfresco"
    assert_that(host.file("/var/log/alfresco/share.log").exists)

def test_share_context_200(host, get_ansible_vars):
    "Check that /share context is available and returns a HTTP 200 status code"
    cmd = host.run("curl -iL --user admin:admin --connect-timeout 5 http://{}:8080/share".format(test_host))
    assert_that(cmd.stdout, contains_string("Alfresco Share"))
    assert_that(cmd.stdout, contains_string("HTTP/1.1 200"))

def test_vti_bin_context_200(host, get_ansible_vars):
    "Check that /share context is available and returns a HTTP 200 status code"
    cmd = host.run("curl -iL --user admin:admin --connect-timeout 5 http://{}:8080/_vti_bin/".format(test_host))
    assert_that(cmd.stdout, contains_string("Welcome to Alfresco!"))
    assert_that(cmd.stdout, contains_string("This application does not provide a web interface in the browser."))
    assert_that(cmd.stdout, contains_string("HTTP/1.1 200"))

def test_vti_inf_context_200(host, get_ansible_vars):
    "Check that /share context is available and returns a HTTP 200 status code"
    cmd = host.run("curl -iL --user admin:admin --connect-timeout 5 http://{}:8080/_vti_inf.html".format(test_host))
    assert_that(cmd.stdout, contains_string("_vti_bin"))
    assert_that(cmd.stdout, contains_string("FrontPage Configuration Information"))
    assert_that(cmd.stdout, contains_string("HTTP/1.1 200"))

def test_api_explorer_context_200(host, get_ansible_vars):
    "Check that /api-explorer context is available and returns a HTTP 200 status code"
    cmd = host.run("curl -iL --user admin:admin http://{}:8080/api-explorer".format(test_host))
    assert_that(cmd.stdout, contains_string("Alfresco Content Services REST API Explorer"))
    assert_that(cmd.stdout, contains_string("HTTP/1.1 200"))
