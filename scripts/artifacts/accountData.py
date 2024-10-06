__artifacts_v2__ = {
    "get_accs": {
        "name": "Account Data",
        "description": "Extract information about configured user accounts",
        "author": "@AlexisBrignoni",
        "version": "0.2",
        "date": "2023-11-21",
        "requirements": "none",
        "category": "Accounts",
        "notes": "",
        "paths": ('*/mobile/Library/Accounts/Accounts3.sqlite*'),
        "output_types": "all"
    }
}


from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly, convert_ts_human_to_timezone_offset

@artifact_processor
def get_accs(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    data_headers = ()
    source_path = ''

    for file_found in files_found:
        source_path = str(file_found)    
        if file_found.endswith('Accounts3.sqlite'):
            break
    
    if not source_path:
        logfunc('Accounts3.sqlite not found')
        return data_headers, data_list, source_path

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()

    cursor.execute('''
    SELECT
        datetime(zdate+978307200,'unixepoch'),
        zaccounttypedescription,
        zusername,
        zaccountdescription,
        zaccount.zidentifier,
        zaccount.zowningbundleid
    FROM zaccount, zaccounttype 
    WHERE zaccounttype.z_pk=zaccount.zaccounttype
    ''')

    all_rows = cursor.fetchall()

    if len(all_rows) > 0:
        for row in all_rows:
            timestamp = convert_ts_human_to_timezone_offset(row[0], timezone_offset)
            data_list.append((timestamp,row[1],row[2],row[3],row[4],row[5]))                
    else:
        logfunc("No account data found")

    db.close()

    data_headers = (
        ('Timestamp', 'datetime'), 
        'Account Desc.', 
        'Username', 
        'Description', 
        'Identifier', 
        'Bundle ID'
        )
    return data_headers, data_list, source_path
