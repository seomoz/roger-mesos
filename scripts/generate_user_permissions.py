#--------------------------------------------------------------------------------
# Run this script as follow, it can only read from Google Docs
#
# Requires packages:
#                   1. gspread
#                   2. oauth2client
#
# python generate_user_permissions.py -f  "oath_credentials.json" 
#                                     -ss "google_user_spreadsheet_permissions"
#                                     -ss "google_bot_spreadsheet_permissions"
#--------------------------------------------------------------------------------
import json
import sys 
import os 
import argparse
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--oauth_credentials_file", help="Path of the file where oauth credentials to " +
                    "access google drive API is stored, Make sure the email in this file " + 
                    "has read access on the spreadsheets")
    parser.add_argument('-ss', "--spreadsheet_title", action='append')
    parser.add_argument('-p', '--password_column_name', help="Name of the column in the spreadsheet which has password,"+
                        "if not specified password is same as username", nargs='?', default="username" )
    args = parser.parse_args()
    sheet_titles = args.spreadsheet_title
    password_column = args.password_column_name
    oauth_credentials_file = args.oauth_credentials_file
    user_permission_rows = getUserPermissionRows(sheet_titles, oauth_credentials_file)
    users_json = generateUserPermissionsJson(user_permission_rows, password_column)
    filename = 'user-permissions.json'    
    writeJsonToFile(users_json, filename)

    #-------------------------------------------------------------------------------
    # This code reads user permissions from a spread sheet as of now, the source can
    # changed easily as long as it returns rows in following format.
    # 
    #  {"username":"jon", "team":"watch", "path":"/winterfell/", 
    #   "create":"allowed", "update":"allowed", "delete":"allowed", 
    #   "view":"allowed", "killTask":"allowed"
    #
    #-------------------------------------------------------------------------------    

def getUserPermissionRows(sheet_titles, oauth_credentials_file):
    scope = ['https://spreadsheets.google.com/feeds']
    # Currently, the email defined under this file has to have edit permissions on the file
    # todo : check if we can get rid of that and use our email instead of the generated
    credentials = ServiceAccountCredentials.from_json_keyfile_name(oauth_credentials_file, scope)
    gc = gspread.authorize(credentials)

    # open by title - titles can change and so is fragile, keys don't
    # this works as well
    # gc.open_by_key("1Izpq1eZI1NuMBddpvvxsIt3usWm11j56eJwPdfxCw6E").sheet1
    rows = []
    for title in sheet_titles:
        sheet = gc.open(title).sheet1
        rows = rows + sheet.get_all_records() 
    return rows
    #-------------------------------------------------------------------------------


def generateUserPermissionsJson(rows, password_column):
    multiple_user_permissions_per_user = {}
    user_permissions_json = []
    actions = ["create", "update", "delete", "view", "killTask"]
    permissions_json = {}
    credentials = {}

    for row in rows:
        # todo : "username" and "path" are required keys, bailout if they are not defined
        # dictionary with keys username, team, path, create, update, delete, view, killTask
        actions_allowed = []
        user = row["username"]
        if (not row["path"]):
            continue
        # remove spaces from key and values 
        row = {k.translate(None, ' '): v.translate(None, ' ') for k, v in row.iteritems()}
        if any(action in row.keys() for action in actions):
            # user custom permissions        
            if ("create" in row.keys() and row["create"] == "allowed"): actions_allowed.append("create")
            if ("update" in row.keys() and row["update"] == "allowed"): actions_allowed.append("update")
            if ("delete" in row.keys() and row["delete"] == "allowed"): actions_allowed.append("delete")
            if ("view" in row.keys() and row["view"] == "allowed") : actions_allowed.append("view")
            if ("killTask" in row.keys() and row["killTask"] == "allowed"): actions_allowed.append("killTask")
        else:
            actions_allowed = actions

        for action in actions_allowed:    
            permission = {}
            permission["allowed"] = action
            permission["on"] = row["path"]
            if (user not in permissions_json.keys()):
                permissions_json[user] = []
            permissions_json[user].append(permission) 

        if ( not credentials.get(user)):
            credentials[user] = row[password_column]
                
    for user, password in credentials.iteritems():
        user_permissions_json.append ({"user": user.lower(), "password": password, "permissions": permissions_json[user]})

    users_json = {"users": user_permissions_json}
    return users_json

def writeJsonToFile(json_to_write, filename):
    with open(filename, 'w') as outfile:
        json.dump(json_to_write, outfile, indent=4, sort_keys=True)
    print "Successfully generated Json file - %s" % os.getcwd()  + "/" + filename
                
if __name__ == "__main__":
    main()
