# alx_travel_app_0x00
# Travel App API

A Django-based web application for managing travel property listings, bookings, and reviews.

## Features

- User authentication and registration
- Create, update, and view property listings
- Book listings for specific dates
- Leave reviews and ratings on listings
- RESTful API endpoints for all major resources


### Prerequisites

- Python 3.8+
- pip
- Virtualenv (recommended)
- Django (see requirements.txt)

### Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/travel-listings-app.git
   cd travel-listings-app
   ```

2. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Apply migrations:**
   ```sh
   python manage.py makemigrations
   python manage.py migrate
   ```
   

5. **Create a superuser (optional, for admin access):**
   ```sh
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```sh
   python manage.py runserver
   ```

7. **(Optional) Seed the database with sample data:**
   ```sh
   python manage.py seed
   ```


- Access the app at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Admin panel at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- API endpoints are available under `/api/`

## Project Structure

```
travel-listings-app/
│   manage.py
│   requirements.txt
│   README.md
└───listings/
    │   models.py
    │   serializers.py
    │   views.py
    │   urls.py
    └───management/
        └───commands/
            │   seed.py
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a pull request

## License

This project is licensed under the MIT License.
