import openai
from PIL import Image, ImageDraw, ImageFont
import datetime
import os

openai.api_key = "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"

def collect_user_inputs():
    """Collect user inputs for the sports event schedule including start and end dates"""
    print("Let's plan your sports event trip!")
    start_date = input("Enter trip start date (YYYY-MM-DD, e.g., 2025-03-31): ")
    try:
        start_date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    except ValueError:
        print("Invalid start date format. Using today's date as default.")
        start_date_obj = datetime.datetime.now()
        start_date = start_date_obj.strftime('%Y-%m-%d')
    
    end_date = input("Enter trip end date (YYYY-MM-DD, e.g., 2025-04-02): ")
    try:
        end_date_obj = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        if end_date_obj < start_date_obj:
            raise ValueError("End date must be after start date.")
    except ValueError as e:
        print(f"Invalid end date: {e}. Using 3 days from start date as default.")
        end_date_obj = start_date_obj + datetime.timedelta(days=3)
        end_date = end_date_obj.strftime('%Y-%m-%d')
    
    location = input("Enter event location (e.g., 'Riyadh, Saudi Arabia'): ")
    has_ticket = input("Do you have a ticket already? (yes/no): ").lower() == 'yes'
    
    ticket_details = None
    if has_ticket:
        ticket_details = input("Enter your ticket details (e.g., event name, date, time, seat): ")
    
    preferences = input("Enter your preferences (e.g., 'local food, museums, fan meetups'): ")
    
    duration = (end_date_obj - start_date_obj).days + 1
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "duration": duration,
        "location": location,
        "has_ticket": has_ticket,
        "ticket_details": ticket_details,
        "preferences": preferences
    }

def generate_itinerary(inputs):
    """Generate itinerary using GPT-4-turbo with specific date range"""
    prompt = f"""
    Create a detailed sports event schedule for a fan with the following details:
    - Trip start date: {inputs['start_date']}
    - Trip end date: {inputs['end_date']}
    - Duration: {inputs['duration']} days
    - Location: {inputs['location']}
    - Ticket status: {'Has ticket' if inputs['has_ticket'] else 'Needs ticket'}
    - Ticket details: {inputs['ticket_details'] if inputs['has_ticket'] else 'N/A'}
    - Preferences: {inputs['preferences']}
    
    Include:
    1. Event timings (align with ticket details if provided, otherwise make reasonable assumptions within the date range)
    2. Travel time estimates between locations
    3. Nearby attractions, food places, or fan events based on preferences
    4. If no ticket, suggest ticket sources or alternatives
    
    Format the response as a list of entries, each with a date, time, and activity, separated by newlines.
    Use '||' as the delimiter between date, time, and activity.
    Example format:
    2025-03-31||12:00 PM||Arrive in Riyadh
    2025-03-31||2:00 PM||Check into hotel (est. 30 min travel)
    Ensure all activities fit within the specified date range.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    
    return response.choices[0].message.content

def create_schedule_image(itinerary_text, output_filename="schedule.png"):
    """Create a visual schedule image as a table using PIL"""
    # Parse the itinerary text
    lines = [line.strip() for line in itinerary_text.split('\n') if line.strip()]
    data = [line.split('||') for line in lines if len(line.split('||')) == 3]
    n = len(data)
    
    if n == 0:
        print("No itinerary data found.")
        return
    
    # Table settings
    col_widths = [150, 100, 500]  # Widths for Date, Time, Activity
    row_height = 40
    start_x = 50
    table_start_y = 100
    image_width = 850
    image_height = 100 + (n + 1) * row_height + 50  # Dynamic height
    background_color = (255, 245, 230)  # Light beige
    header_bg_color = (200, 200, 200)  # Light gray
    even_row_bg_color = (255, 255, 255)  # White
    odd_row_bg_color = (240, 240, 240)  # Very light gray
    text_color = (0, 0, 0)  # Black
    header_text_color = (0, 0, 100)  # Dark blue
    line_color = (150, 150, 150)  # Gray
    
    # Create the image
    image = Image.new('RGB', (image_width, image_height), background_color)
    draw = ImageDraw.Draw(image)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 36)
        header_font = ImageFont.truetype("arial.ttf", 24)
        text_font = ImageFont.truetype("arial.ttf", 20)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Draw the title
    draw.text((50, 50), "Your Sports Event Schedule", font=title_font, fill=header_text_color)
    
    # Draw header background
    draw.rectangle([start_x, table_start_y, start_x + sum(col_widths), table_start_y + row_height], fill=header_bg_color)
    
    # Draw row backgrounds with alternating colors
    for i in range(n):
        bg_color = even_row_bg_color if i % 2 == 0 else odd_row_bg_color
        y_top = table_start_y + (i + 1) * row_height
        draw.rectangle([start_x, y_top, start_x + sum(col_widths), y_top + row_height], fill=bg_color)
    
    # Draw header text
    headers = ["Date", "Time", "Activity"]
    for j, header in enumerate(headers):
        if j == 0:  # Left-aligned
            x = start_x + 10
        elif j == 1:  # Center-aligned
            # Use textlength instead of textsize
            text_width = draw.textlength(header, font=header_font)  
            x = start_x + col_widths[0] + (col_widths[1] - text_width) / 2
        elif j == 2:  # Left-aligned
            x = start_x + sum(col_widths[:2]) + 10
        draw.text((x, table_start_y + 5), header, font=header_font, fill=header_text_color)
    
    # Draw data text
    for i, row in enumerate(data):
        y = table_start_y + (i + 1) * row_height + 5
        for j, cell in enumerate(row):
            if j == 0:  # Left-aligned
                x = start_x + 10
            elif j == 1:  # Center-aligned
                # Use textlength instead of textsize
                text_width = draw.textlength(cell, font=text_font)  
                x = start_x + col_widths[0] + (col_widths[1] - text_width) / 2
            elif j == 2:  # Left-aligned
                x = start_x + sum(col_widths[:2]) + 10
            draw.text((x, y), cell, font=text_font, fill=text_color)
    
    # Draw grid lines
    for i in range(n + 2):  # Horizontal lines
        y = table_start_y + i * row_height
        draw.line([(start_x, y), (start_x + sum(col_widths), y)], fill=line_color)
    
    x_positions = [start_x] + [start_x + sum(col_widths[:k+1]) for k in range(len(col_widths))]
    for x in x_positions:  # Vertical lines
        draw.line([(x, table_start_y), (x, table_start_y + (n + 1) * row_height)], fill=line_color)
    
    # Save the image
    image.save(output_filename)
    print(f"Schedule saved as {output_filename}")
    return image

def main():
    # Collect inputs
    user_inputs = collect_user_inputs()
    
    # Generate itinerary using GPT-4-turbo
    print("\nGenerating your schedule...")
    itinerary = generate_itinerary(user_inputs)
    print("\nGenerated Schedule:")
    print(itinerary)
    
    # Confirm image generation
    generate_image = input("\nWould you like to generate a schedule image? (yes/no): ").lower() == 'yes'
    if generate_image:
        create_schedule_image(itinerary)
        # Optionally display the image (uncomment if desired)
        # Image.open("schedule.png").show()