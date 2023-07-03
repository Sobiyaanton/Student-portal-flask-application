from flask import Flask, render_template, request, redirect, url_for, session
import boto3
import key_config as keys
import dynamoDB_create_table as dynamodb_ct
import decimal

app = Flask(__name__)
app.secret_key = 'MOkJTyO4sWk5tDRQY/LJL98SOrKDamKzfPr9t+p7'

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=keys.ACCESS_KEY_ID,
    aws_secret_access_key=keys.ACCESS_SECRET_KEY,
    region_name=keys.REGION_NAME,
)

s3= boto3.resource(
    's3',
    aws_access_key_id=keys.ACCESS_KEY_ID,
    aws_secret_access_key=keys.ACCESS_SECRET_KEY,
    region_name=keys.REGION_NAME,
)

from boto3.dynamodb.conditions import Key, Attr

@app.route('/')
def root_route():
    #dynamodb_ct.create_table()
    #return 'Table created'
    return render_template('signup.html')
    
# Route for the signup page
@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        # Retrieve form data
        full_name = request.form['full_name']
        registration_number = int(request.form['registration_number'])
        email = request.form['email']
        password = request.form['password']
        degree = request.form['degree']
        contact_number = request.form['contact_number']
        introduction = request.form['introduction']
        skills = request.form['skills']

        table = dynamodb.Table('students')
        
        # Store student data in DynamoDB
        table.put_item(
            Item={
                'full_name': full_name,
                'registration_number': registration_number,
                'email': email,
                'password': password,
                'degree': degree,
                'contact_number': contact_number,
                'introduction': introduction,
                'skills': skills,
            }
        )
        msg = "Registration Complete. Please Login to your account!"
        return render_template('login.html',msg = msg)
    return render_template('signup.html')
    
@app.route('/login')
def login():    
    return render_template('login.html')
    
@app.route('/check', methods=['POST'])
def check():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        table = dynamodb.Table('students')
        response = table.scan(
            FilterExpression=Attr('email').eq(email)
        )
        items = response['Items']

        if len(items) > 0:
            full_name = items[0]['full_name']
            registration_number = items[0]['registration_number']
            stored_password = items[0]['password']

            if password == stored_password:
                return render_template("profile-edit.html", students=items[0])

    return render_template("login.html")


import urllib.parse

@app.route('/update-profile', methods=['POST', 'GET'])
def update_profile():
    if request.method == 'POST':

        # Check if an image file is included in the request
        if 'myimage' in request.files:
            file = request.files['myimage']
            if file.filename != '':
                filename = file.filename
                bucket_name = 'sobi-bucket-test'
                bucket = s3.Bucket(bucket_name)
                bucket.put_object(
                    Key=filename,
                    Body=file,
                    ContentType='image/jpeg',
                    ContentDisposition='inline'
                )

                # Generate object URL
                encoded_object_key = urllib.parse.quote(filename)
                object_url = f"https://{bucket_name}.s3.amazonaws.com/{encoded_object_key}"
            else:
                object_url = None
        else:
            object_url = None

        # Retrieve form data
        full_name = request.form['full_name']
        registration_number = int(request.form['registration_number'])  # Convert to int if necessary
        email = request.form['email']
        degree = request.form['degree']
        contact_number = request.form['contact_number']
        introduction = request.form['introduction']
        skills = request.form['skills']

        # Perform the necessary update operations
        table = dynamodb.Table('students')
        update_expression = 'SET full_name = :full, degree = :degree, contact_number = :contact, introduction = :intro, skills = :skills'
        expression_attribute_values = {
            ':full': full_name,
            ':degree': degree,
            ':contact': contact_number,
            ':intro': introduction,
            ':skills': skills,
        }

        if object_url is not None:
            update_expression += ', profile_image_url = :image_url'
            expression_attribute_values[':image_url'] = object_url

        response = table.update_item(
            Key={
                'registration_number': registration_number,
                'email': email,
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues='ALL_NEW'  # Retrieve the updated data
        )

        updated_student = response['Attributes']

        return render_template('profile-view.html', students=updated_student)

    return render_template('profile-edit.html')


@app.route('/view-profile/<int:registration_number>', methods=['GET'])
def profile_view(registration_number):
    registration_number = int(registration_number)
    table = dynamodb.Table('students')
    response = table.get_item(
        Key={
            'registration_number': registration_number
        }
    )
    students = response.get('Item', {})  # Set students as an empty dictionary if no data is found

    return render_template('profile-view.html', students=students)

@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()

    # Redirect the user to the login page
    return redirect(url_for('login'))
    
if __name__ == '__main__':
    app.run(debug=True,port=8080,host='0.0.0.0')