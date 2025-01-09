# 📸 PhotoShare
<br/>
Welcome to PhotoShare - a REST API project built by The Byte Brygade Team
<br/>

## 📚 Table of contents
- [Technologies](#technologies-used)
- [Installation](#installation)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Usage](#usage)
<br/>

## ⚙ Technologies used
### Backend
- 🐍 Python
- 🐳 Docker
- ☁️ Cloudinary
- 🛢️ Redis
- 📜 Poetry
- 📜 SQLAlchemy
- 📜 Alembic

### Frontend
- 🇹🇸 Typescript
- ⚛️ React
- #️⃣ Next.js
- #️⃣ Node.js
- ➰ Tailwind CSS
- ⸝⸝⸝ shadcn/ui

<br/>

## 🛠 Installation
Instruction on how to install and set up the project.

Before you begin, make sure you have the following configuration installed on your system:

- Git
- Python **3.12** or later
- **pip** and **poetry** -> Python package manager
- Docker
- Node.js **18.18** or later
- **npm** and **pnpm** -> Node package manager 
- You should you should be acquainted with these websites: docker.com, cloudinary.com, redis.io, nodejs.org/en, nextjs.org/docs, ui.shadcn.com

### Clone Repository

Clone the PhotoShare repository to your local machine using of following ways :
```
HTTPS: git@github.com:N0yhz/PhotoShare.git

SSH: git@github.com:N0yhz/PhotoShare.git

GitHub CLI: gh repo clone N0yhz/PhotoShare
```
<br/>

### 📝Backend Setup
### Install Dependencies

Navigate to the cloned repository's directory and install the required dependencies using poetry:

```
cd backend
poetry update
```

### Set Up Environment Variables

You need to set up environment variables for the database connection, Cloudinary API, and JWT secret key. This can be done by creating a `.env` file in the root directory of the project and populating it with the necessary values:

[.env.example](https://github.com/N0yhz/PhotoShare/blob/dev/.env.example)
```
# Database
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_HOST=
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/${POSTGRES_DB}

# Email
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=
MAIL_PORT=
MAIL_SERVER=
MAIL_FROM_NAME=

# Cloudinary configuration
CLOUDINARY_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
CLOUDINARY_URL=

# Redis
REDIS_HOST=
Redis_PORT=


#KEYS
SECRET_KEY=
ALGORITHM=
```
**Note:** Ensure to keep your `.env` file secure and never commit it to the repository to protect sensitive information.

Despite that you also have to update your variables in config file: 
```
backend\src\conf\config.py
```

## Run the application
Run the PhotoShare application using uvicorn with the following command:

```
poetry run uvicorn main:app --host localhost --port 8000 --reload
```
### 🐳 Docker Setup

You can also run the PhotoShare application using Docker. First, build the Docker image using the following command:

#### Build Docker Image
```
docker-compose build
```
This command builds a Docker image based on the instructions in the `docker-compose.yml and Dockerfile`

#### Run the Docker Container
Once the image is built, you can run the application inside a Docker container using the following command:
```
docker-compose up -d
```
This command runs all project images in a detached mode (`-d`)

After that you can now access the OpenAPI Documentation `http://localhost:8000/docs`
<br/>

### Data model migration
Before you begin testing routes, you have to make **data models migration** using the folloing command:
```
alembic upgrade head
```
Now you can freeely access all the routes to test.


## 📝Frontend Setup

### Set up Next.js
Before running the server make sure that you have installed **pnpm** manager
If not you can do run this command in terminal:
```
npm install -g pnpm
```

### Run the page
If you stay at folder **frotnend/** direct to -> **photshare-app/**
Run the server using this following command:
```
pnpm run dev
```
After that you can now access the WebApplication at `http://localhost:3000` or `http://127.0.0.1:3000`

## 📜Usage
- Create a new account by clicking **Register** on the right top
- After that you can login to the Phortoshare-web, then you have full access
- You can create a new post by uploading a new image in **Gallery or Post Edit**
- If you want to add **tags** to your post, you can access it by clicking on your post and there would an input area. But the limit is **5 tags/post**
- In the **Gallery** you can access to all posts on the web from every user, it generates like an album only "images" no desctiptions.
- **Explore section**, here you can search or filter the posts by tags. On this page you can also create a new tag if you want
- For the web there is **Image Edit** section where you can add filters to any post you like. It will generate you the **preview, link and qr-code**
- **Post Edit** section here you can edit your post description or even delete the post.
- By clicking on your avatar in the right top corner, you can accees to **settings or profile**
- **Profile**, on this page it will show all your data and posts
- In **Settings** you can change your "username, first_name, last_name, bio"

#### Lastly, always stay positive - share your beautiful memories with others.




### 👨‍💻 Creators

- [Project Manager - Vladyslav Babenko](https://github.com/vlad-bb)
- [TeamLead - Tunh Zyonh Vu](https://github.com/N0yhz)
- [Scrum Master - Stanislav](https://github.com/Nimris)
- [Developer - Pavlo Dovbui](https://github.com/pavlodubovyi)
- [Developer - Helya](https://github.com/Helya-B)
- [Developer - Tatiana](https://github.com/Tig-13)
- [Developer - Roman Harbaż](https://github.com/RHA1705)

## 🤝 Contributing
Contributions are welcome! Please follow the Commonly Recognized Contribution Guidelines 😺

## 📄 License
This project should be licensed under the MIT License.