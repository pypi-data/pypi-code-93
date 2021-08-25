from loginid import LoginID

# directweb application
BASE_URL = "http://localhost:8080/api/native"
CLIENT_ID ="l330ZWseeoJ3ooxHh0yz41s_3oYwYwVuTVt7J16djCgJ_56lYpMIXKPGpmYFQl3-trR34N0Wa3nHXpwZ8ga4wA=="
PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgwX3F5DgjQd9QlPmA
3wWtyoNltn5v+Gv02o8Zw4TF5ImhRANCAARH+9hX50YVg+TNVXSiCwN7thZBF5op
MHh9+toI5ZQPK0OdcuhbzVWuDpMRm9ivx3xAQBrRkCCDd5bG8Ba9lJo2
-----END PRIVATE KEY-----"""


# user info
USERNAME = "John.Doe.Quang"
USER_ID = "2ed409e8-e34c-4949-b074-4e0c2b52b0aa"

lAdmin = LoginID(CLIENT_ID, PRIVATE_KEY, base_url=BASE_URL)

# test helper functions
print("="*50)
print("Test `generateToken`")
print(lAdmin.generateServiceToken("codes.generate")) 

print("="*50)
print("test `decodeToken`")
token = "eyJhbGciOiJFUzI1NiIsImtpZCI6IjBiYTU5NTE0LTA5MDUtNDZjYS1hMDJhLWJkMWM2MDk4YjJhMCIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJsb2dpbmlkLmlvIiwic3ViIjoiMmVkNDA5ZTgtZTM0Yy00OTQ5LWIwNzQtNGUwYzJiNTJiMGFhIiwic2lkIjoiNTQ4NTdhMWQtZDI0Ni00Njc1LWE5MmItMzNjYmRkZjE5YmZjIiwibmlkIjoiNDAxYzRiZWViNzkyNTg1MiIsImF1ZCI6ImwzMzBaV3NlZW9KM29veEhoMHl6NDFzXzNvWXdZd1Z1VFZ0N0oxNmRqQ2dKXzU2bFlwTUlYS1BHcG1ZRlFsMy10clIzNE4wV2EzbkhYcHdaOGdhNHdBPT0iLCJhY3Rpb24iOiJsb2dpbiIsImlhdCI6MTYyMzI2Nzk3NiwidWRhdGEiOiJKb2huLkRvZS5RdWFuZyJ9.zNwZ3j8YhfTHkzPDJkfR24Q0nYJ8roqEzbEmeACCZ0XmwJdlzLANfxcmD4tthB57pwrHvkXpsuWoNpdl9QEr4w"
print(lAdmin.verifyToken(token))

# Code APIs
# common settings
codeType = 'short'
codePurpose = 'temporary_authentication'

# waitCode function will stall the test flow. 
# enable this variable to test waitCode
TEST_WAIT_CODE = False

print("="*50)
print("test `generateCode`")
err, code_response = lAdmin.generateCode(USER_ID, codeType, codePurpose, False)

if err is not None:
    print(err, code_response)
else:
    print(code_response)

print("="*50)
print("test `authorizeCode`")
err, response = lAdmin.authorizeCode(USER_ID, code_response['code'], codeType, codePurpose)

if err is not None:
    print(err, response)
else:
    print(response)

print("="*50)
print("test `invalidateAllCodes`")
# generate some code to invalidate
err, code_response = lAdmin.generateCode(USER_ID, "short", "temporary_authentication", False)

if err is not None:
    print('failed to generate code')
    print(err, code_response)
else:
    print('code generated', code_response)
    print('invalidate code')
    print(lAdmin.invalidateAllCodes(USER_ID, codeType, codePurpose))

print("="*50)
if TEST_WAIT_CODE:

    print("test `waitCode`")
    # generate some code to invalidate
    err, code_response = lAdmin.generateCode(USER_ID, "short", "temporary_authentication", False)

    if err is not None:
        print('failed to generate code')
        print(err, code_response)
    else:
        print('code generated', code_response)
        print('waiting for code to be authorized')
        err, response = lAdmin.waitCode(USERNAME, code_response['code'], codeType)
        print(response)
else:
    print("TEST_WAIT_CODE is False, skipping waitCode test")

# Transaction Flow
sample_payload = "A sample payload"
print("="*50)
print("test `generateTxAuthToken`")
print(lAdmin.generateTxAuthToken(sample_payload, USERNAME))

print("="*50)
print("test `createTxId`")
err, response = lAdmin.createTxId(sample_payload, USERNAME)
if err is not None:
    print(err, response)
else:
    print('tx_id', response)