from app import create_app

app = create_app()

app.config['UPLOAD_FOLDER'] = # ADD CMS LOCATION HERE

if __name__ == '__main__':
    app.run(debug=True)
    
