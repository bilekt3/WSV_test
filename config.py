"""Configuration parameters for each site."""

config = [
    ("North_Europe", "https://www.websupervisor.net/", "you_name_here", 15),
    ("Australia", "https://aus.websupervisor.net/", "you_name_here", 4),
]

xpath_username = '//*[@id="microsite-login-name"]'
xpath_password = '//*[@id="microsite-login-password"]'
xpath_login = '//*[@id="intro"]/div[1]/div/div[1]/div/form/div[3]/input'
xpath_login_id = (
    "/html/body/div[4]/div/div[1]/div[1]/div/header/div[2]/ul/li[1]/span[1]"
)
xpath_units = '//*[@id="main-menu-nav"]/ul/li[2]/a'

ERP_url = 'https://comap-control.operations.dynamics.com/'

status_file = "status.yaml"

test_enabled = True
send_to_teams = True
