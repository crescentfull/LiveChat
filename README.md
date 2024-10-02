
# LiveChat Project

## Overview
LiveChat is a real-time chat application built using Django and Django Channels. This project supports user authentication, chat room creation, and real-time message exchange based on WebSocket.

## Project Structure
```
liveChat/
│
├── liveChat/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│
├── myapp/
│   ├── migrations/
│   ├── templates
│       ├── base.html
│       ├── chat_room_detail.html
│       ├── chat_room_list.html
│       ├── index.html
│       └── register.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── consumers.py
│   ├── models.py
│   ├── routing.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│
├── manage.py
└── .env
```

## Key Features
1. **User Authentication**: Sign up, log in, and log out.
2. **Chat Rooms**:
   </br> - Only registered users can create and delete rooms.
   </br> - Error logs and login logs are enabled.
3. **Real-time Messaging**: Supports WebSocket-based real-time messaging using Django Channels.
4. **Anonymous Chatting**: Users can participate in chat rooms anonymously if they are not registered. They will be assigned a number in the format of Anonymous1, 2, ..., n in the order of participation.
5. **Database**: Interacts with the database using Django's ORM.

## Installation

### Prerequisites
- Python 3.x
- Django 4.x
- Django Channels, Redis
- MySQL (or another database supported by Django)

### Installation Steps
1. Clone the repository:
    ```
    git clone <https://github.com/crescentfull/LiveChat.git>
    ```
2. Navigate to the project directory:
    ```
    cd liveChat
    ```
3. Create and activate a virtual environment:
    ```
    python -m venv venv
    source venv/bin/activate  # On Windows: `venv\Scripts\activate`
    ```
4. Install the required packages:
    ```
    pip install -r requirements.txt
    ```
5. Set environment variables in the `.env` file in the root directory:
    ```
    DJANGO_SECRET_KEY=<your-secret-key>
    DATABASE_NAME=<your-database-name>
    DATABASE_USER=<your-database-user>
    DATABASE_PASSWORD=<your-database-password>
    ```
6. Apply migrations:
    ```
    python manage.py migrate
    ```
7. Run the development server:
    ```
    python manage.py runserver
    ```

## Usage
- Access the application at `http://localhost:8000`.
- Register a new user or log in.
- Create chat rooms and exchange messages in real-time.

## Directory Details
- **liveChat/**: Main project directory that includes settings and ASGI configuration.
  - `asgi.py`: Contains the ASGI settings to enable WebSocket communication.
- **myapp/**: Core application that handles chat functionalities.
  - `models.py`: Defines the `ChatRoom` and `Message` models for the database.
  - `views.py`: Includes views that handle user interactions, such as listing and joining chat rooms.
  - `consumers.py`: Defines WebSocket consumers for real-time messaging.
  - `routing.py`: Configures WebSocket URL routing.

## WebSocket Configuration
WebSocket connections are managed using Django Channels and the `ChatConsumer` in `myapp/consumers.py`. It handles chat room connections, message exchanges, and user entry/exit notifications.

## License
This project is licensed under the MIT License.
