"""
Veritabanı başlatma script'i
Render'da ilk deploy'dan sonra veya manuel olarak çalıştırılabilir
"""
from app import app, db, User

with app.app_context():
    # Tüm tabloları oluştur
    db.create_all()
    print("Veritabanı tabloları oluşturuldu.")
    
    # Admin kullanıcısı yoksa oluştur
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            is_admin=True,
            can_add=True,
            can_edit=True,
            can_delete=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin kullanıcısı oluşturuldu: admin / admin123")
    else:
        print("Admin kullanıcısı zaten mevcut.")

