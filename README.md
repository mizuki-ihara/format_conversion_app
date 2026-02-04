# format_conversion_app
Compare training and test data and fix their format types if they are different

usage:
1. Install DRApps
> pip install git+https://github.com/datarobot/dr-apps
2. Run the following command to register the app on DataRobot Registry
>> drapps create -t %YOUR_TOKEN% -e "[Experimental] Python 3.9 Streamlit" -p ./ %APP_NAME%
Replace %YOUR_TOKEN% with your token, and %APP_NAME% with your application name. 