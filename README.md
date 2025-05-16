# Family Helper App

An AI-powered application to assist with family meal prep and photoshoot booking.

## Features

- AI-powered Weekly Meal Planning
  - Customizable for family size
  - Dietary restriction support
  - Healthy meal suggestions

- Shoott Photography Booking Assistant
  - Studio finder by location
  - Availability checking
  - Book appointment

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Meal Prep Tab:
   - Select family size using the slider
   - Enter any dietary restrictions
   - Click "Generate Weekly Menu" to get a personalized meal plan

2. Shoott Photography Booking Tab:
   - Enter your desired location
   - Select your preferred date
   - Choose the number of family members
   - Click "Find Photoshoot Studios" to see available options
   - View studio details including address, price, rating, and availability
   - Click "Book with Shoott Photography" to start the booking process
   - Choose number of family members
   - View available studios and prices

The app uses OpenAI's GPT-3.5 for meal planning and provides a user-friendly interface for Shoott photoshoot booking.

## Future Development Tasks

1. **Family Preferences Enhancements**
   - Implement external database storage (e.g., Firebase, MongoDB) for persistent family preferences
   - Add user authentication to support multiple family profiles
   - Improve preference management with profile pictures and more detailed health information

2. **Shoott API Integration**
   - Connect to the official Shoott Photography API
   - Implement real-time availability checking
   - Add direct booking functionality without leaving the app
   - Support payment processing

3. **General Improvements**
   - Add mobile-responsive design
   - Implement email notifications for meal plans and bookings
   - Add recipe saving and favoriting functionality
   - Create a shopping list export feature (PDF, email, etc.)

4. **Integration with Calendar**
   - Integrate with Google Calendar or Apple Calendar to automatically add meal prep and photoshoot appointments
   
