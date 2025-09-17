#!/usr/bin/env python3
"""
Script to seed the database with default chakra points data.
Run this script after running the migration to populate the chakra_points table.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pymysql
from datetime import datetime

def seed_chakra_points():
    """Seed the database with default chakra points data"""
    
    # Default chakra points data
    chakra_points_data = [
        # East Direction (E1-E8)
        {
            "id": "E1",
            "name": "East 1 - Main Entrance",
            "direction": "East",
            "description": "The main entrance area in the east direction. This is considered highly auspicious for the main door of the house.",
            "remedies": "Keep this area clean and well-lit. Place a water fountain or plant here. Avoid heavy furniture or clutter.",
            "is_auspicious": True,
            "should_avoid": False
        },
        {
            "id": "E2",
            "name": "East 2 - Living Room",
            "direction": "East",
            "description": "Living room area in the east direction. Ideal for family gatherings and social activities.",
            "remedies": "Use light colors, ensure good ventilation. Place plants or water elements. Avoid dark colors or heavy furniture.",
            "is_auspicious": True,
            "should_avoid": False
        },
        {
            "id": "E3",
            "name": "East 3 - Study Room",
            "direction": "East",
            "description": "Study or work area in the east direction. Excellent for concentration and learning.",
            "remedies": "Keep books organized, use natural light. Place a small water fountain. Avoid clutter or dark corners.",
            "is_auspicious": True,
            "should_avoid": False
        },
        {
            "id": "E4",
            "name": "East 4 - Prayer Room",
            "direction": "East",
            "description": "Prayer or meditation room in the east direction. Most auspicious for spiritual activities.",
            "remedies": "Keep clean and peaceful. Use light colors, place idols facing east. Avoid any negative energy sources.",
            "is_auspicious": True,
            "should_avoid": False
        },
        {
            "id": "E5",
            "name": "East 5 - Guest Room",
            "direction": "East",
            "description": "Guest room in the east direction. Good for hosting visitors and maintaining relationships.",
            "remedies": "Keep well-ventilated, use comfortable furniture. Place fresh flowers. Avoid heavy or dark furniture.",
            "is_auspicious": True,
            "should_avoid": False
        },
        {
            "id": "E6",
            "name": "East 6 - Balcony",
            "direction": "East",
            "description": "Balcony or terrace in the east direction. Great for morning activities and fresh air.",
            "remedies": "Keep clean and open. Place plants or flowers. Avoid clutter or storage items.",
            "is_auspicious": True,
            "should_avoid": False
        },
        {
            "id": "E7",
            "name": "East 7 - Garden",
            "direction": "East",
            "description": "Garden or outdoor space in the east direction. Excellent for plants and morning activities.",
            "remedies": "Plant flowering plants, maintain cleanliness. Place a water feature. Avoid thorny plants or clutter.",
            "is_auspicious": True,
            "should_avoid": False
        },
        {
            "id": "E8",
            "name": "East 8 - Storage",
            "direction": "East",
            "description": "Storage area in the east direction. Should be used carefully to avoid blocking positive energy.",
            "remedies": "Keep organized and clean. Use light colors. Avoid storing heavy or negative items.",
            "is_auspicious": False,
            "should_avoid": True
        },
        
        # South Direction (S1-S8)
        {
            "id": "S1",
            "name": "South 1 - Master Bedroom",
            "direction": "South",
            "description": "Master bedroom in the south direction. Good for the head of the family.",
            "remedies": "Use earth tones, ensure good ventilation. Place bed with head towards south. Avoid water elements.",
            "is_auspicious": True,
            "should_avoid": False
        },
        {
            "id": "S2",
            "name": "South 2 - Kitchen",
            "direction": "South",
            "description": "Kitchen in the south direction. Fire element is strong here.",
            "remedies": "Keep clean and well-ventilated. Use fire-resistant materials. Avoid water elements near cooking area.",
            "is_auspicious": True,
            "should_avoid": False
        },
        {
            "id": "S3",
            "name": "South 3 - Dining Room",
            "direction": "South",
            "description": "Dining area in the south direction. Good for family meals and bonding.",
            "remedies": "Use warm colors, ensure good lighting. Place dining table properly. Avoid clutter or dark corners.",
            "is_auspicious": True,
            "should_avoid": False
        },
        {
            "id": "S4",
            "name": "South 4 - Bathroom",
            "direction": "South",
            "description": "Bathroom in the south direction. Should be designed carefully to avoid negative energy.",
            "remedies": "Keep very clean, use light colors. Ensure proper ventilation. Avoid keeping it open or cluttered.",
            "is_auspicious": False,
            "should_avoid": True
        },
        {
            "id": "S5",
            "name": "South 5 - Storage",
            "direction": "South",
            "description": "Storage area in the south direction. Can be used for heavy items.",
            "remedies": "Keep organized, use strong materials. Avoid storing food items. Keep area dry and clean.",
            "is_auspicious": False,
            "should_avoid": False
        },
        {
            "id": "S6",
            "name": "South 6 - Garage",
            "direction": "South",
            "description": "Garage or parking area in the south direction. Suitable for vehicles and heavy items.",
            "remedies": "Keep clean and organized. Use strong flooring. Avoid storing food or water-sensitive items.",
            "is_auspicious": False,
            "should_avoid": False
        },
        {
            "id": "S7",
            "name": "South 7 - Workshop",
            "direction": "South",
            "description": "Workshop or utility area in the south direction. Good for fire-related activities.",
            "remedies": "Ensure good ventilation, use fire-resistant materials. Keep tools organized. Avoid water elements.",
            "is_auspicious": False,
            "should_avoid": False
        },
        {
            "id": "S8",
            "name": "South 8 - Septic Tank",
            "direction": "South",
            "description": "Septic tank or waste area in the south direction. Should be placed carefully.",
            "remedies": "Keep covered and clean. Ensure proper drainage. Avoid placing near living areas.",
            "is_auspicious": False,
            "should_avoid": True
        },
        
        # West Direction (W1-W8)
        {
            "id": "W1",
            "name": "West 1 - Children's Room",
            "direction": "West",
            "description": "Children's bedroom in the west direction. Good for young ones and creativity.",
            "remedies": "Use bright colors, ensure good lighting. Place study table properly. Avoid heavy furniture or dark colors.",
            "is_auspicious": True,
            "should_avoid": False
        },
        {
            "id": "W2",
            "name": "West 2 - Study Area",
            "direction": "West",
            "description": "Study or work area in the west direction. Good for afternoon studies.",
            "remedies": "Ensure good lighting, keep organized. Use light colors. Avoid clutter or distractions.",
            "is_auspicious": True,
            "should_avoid": False
        },
        {
            "id": "W3",
            "name": "West 3 - Guest Room",
            "direction": "West",
            "description": "Guest room in the west direction. Suitable for visitors and temporary stays.",
            "remedies": "Keep comfortable and clean. Use neutral colors. Avoid heavy furniture or dark themes.",
            "is_auspicious": True,
            "should_avoid": False
        },
        {
            "id": "W4",
            "name": "West 4 - Bathroom",
            "direction": "West",
            "description": "Bathroom in the west direction. Should be designed with proper ventilation.",
            "remedies": "Keep very clean, use light colors. Ensure proper drainage. Avoid keeping it open or cluttered.",
            "is_auspicious": False,
            "should_avoid": True
        },
        {
            "id": "W5",
            "name": "West 5 - Storage",
            "direction": "West",
            "description": "Storage area in the west direction. Can be used for seasonal items.",
            "remedies": "Keep organized and dry. Use proper containers. Avoid storing food or water-sensitive items.",
            "is_auspicious": False,
            "should_avoid": False
        },
        {
            "id": "W6",
            "name": "West 6 - Balcony",
            "direction": "West",
            "description": "Balcony or terrace in the west direction. Good for evening activities.",
            "remedies": "Keep clean and open. Place comfortable seating. Avoid clutter or heavy items.",
            "is_auspicious": True,
            "should_avoid": False
        },
        {
            "id": "W7",
            "name": "West 7 - Garden",
            "direction": "West",
            "description": "Garden or outdoor space in the west direction. Good for evening relaxation.",
            "remedies": "Plant suitable plants, maintain cleanliness. Place comfortable seating. Avoid thorny or negative plants.",
            "is_auspicious": True,
            "should_avoid": False
        },
        {
            "id": "W8",
            "name": "West 8 - Utility",
            "direction": "West",
            "description": "Utility area in the west direction. Suitable for maintenance and repair work.",
            "remedies": "Keep organized and clean. Use proper tools storage. Avoid clutter or dangerous items.",
            "is_auspicious": False,
            "should_avoid": False
        },
        
        # North Direction (N1-N8)
        {
            "id": "N1",
            "name": "North 1 - Living Room",
            "direction": "North",
            "description": "Living room in the north direction. Excellent for social activities and wealth.",
            "remedies": "Use light colors, ensure good ventilation. Place water elements. Avoid heavy furniture or dark colors.",
            "is_auspicious": True,
            "should_avoid": False
        },
        {
            "id": "N2",
            "name": "North 2 - Study Room",
            "direction": "North",
            "description": "Study or work area in the north direction. Great for business and career growth.",
            "remedies": "Keep organized, use natural light. Place a small water fountain. Avoid clutter or distractions.",
            "is_auspicious": True,
            "should_avoid": False
        },
        {
            "id": "N3",
            "name": "North 3 - Prayer Room",
            "direction": "North",
            "description": "Prayer or meditation room in the north direction. Good for spiritual practices.",
            "remedies": "Keep clean and peaceful. Use light colors, place idols properly. Avoid any negative energy sources.",
            "is_auspicious": True,
            "should_avoid": False
        },
        {
            "id": "N4",
            "name": "North 4 - Bathroom",
            "direction": "North",
            "description": "Bathroom in the north direction. Should be designed carefully to avoid blocking wealth energy.",
            "remedies": "Keep very clean, use light colors. Ensure proper drainage. Avoid keeping it open or cluttered.",
            "is_auspicious": False,
            "should_avoid": True
        },
        {
            "id": "N5",
            "name": "North 5 - Storage",
            "direction": "North",
            "description": "Storage area in the north direction. Should be used carefully to avoid blocking wealth flow.",
            "remedies": "Keep organized and clean. Use light colors. Avoid storing heavy or negative items.",
            "is_auspicious": False,
            "should_avoid": True
        },
        {
            "id": "N6",
            "name": "North 6 - Garden",
            "direction": "North",
            "description": "Garden or outdoor space in the north direction. Excellent for water features and plants.",
            "remedies": "Plant water-loving plants, place water features. Keep clean and well-maintained. Avoid thorny plants.",
            "is_auspicious": True,
            "should_avoid": False
        },
        {
            "id": "N7",
            "name": "North 7 - Balcony",
            "direction": "North",
            "description": "Balcony or terrace in the north direction. Good for relaxation and fresh air.",
            "remedies": "Keep clean and open. Place comfortable seating. Avoid clutter or heavy items.",
            "is_auspicious": True,
            "should_avoid": False
        },
        {
            "id": "N8",
            "name": "North 8 - Utility",
            "direction": "North",
            "description": "Utility area in the north direction. Should be kept minimal to avoid blocking wealth energy.",
            "remedies": "Keep minimal and clean. Use light colors. Avoid storing heavy or negative items.",
            "is_auspicious": False,
            "should_avoid": True
        }
    ]
    
    # Connect to database
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='brahmavastu'
    )
    
    cursor = conn.cursor()
    
    try:
        # Check if chakra points already exist
        cursor.execute("SELECT COUNT(*) FROM chakra_points")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            print(f"Chakra points already exist in database ({existing_count} records). Skipping seeding.")
            return
        
        # Insert chakra points
        insert_query = """
        INSERT INTO chakra_points (id, name, direction, description, remedies, is_auspicious, should_avoid, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        current_time = datetime.utcnow()
        
        for chakra_data in chakra_points_data:
            cursor.execute(insert_query, (
                chakra_data['id'],
                chakra_data['name'],
                chakra_data['direction'],
                chakra_data['description'],
                chakra_data['remedies'],
                chakra_data['is_auspicious'],
                chakra_data['should_avoid'],
                current_time,
                current_time
            ))
        
        conn.commit()
        print(f"Successfully seeded {len(chakra_points_data)} chakra points into the database.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error seeding chakra points: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    seed_chakra_points()
