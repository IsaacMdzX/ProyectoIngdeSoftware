from app import create_app

app = create_app()

with app.test_client() as c:
    for path in ['/', '/playeras', '/gorras']:
        r = c.get(path)
        print(path, '->', r.status_code)
        html = r.get_data(as_text=True)
        print(html[:500])
        print('---\n')
