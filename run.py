from app import create_app

app = create_app()

app.config['UPLOAD_FOLDER'] = 'static/uploads'

if __name__ == '__main__':
    app.run(debug=True)
    