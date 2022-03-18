from website import create_app

app = create_app()

# Flask runs directly from python 
if __name__ == '__main__':
    app.run(debug=True)