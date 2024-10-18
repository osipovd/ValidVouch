STATE_CHOICES = [
    ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'),
    ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'),
    ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'),
    ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'),
    ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
    ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'),
    ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'),
    ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'),
    ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'),
    ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'),
    ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'),
    ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'),
    ('WI', 'Wisconsin'), ('WY', 'Wyoming')
]

BUSINESS_CATEGORIES = [
    ('', 'All Categories'),
    ('Automotive', 'Automotive'),
    ('Beauty & Spas', 'Beauty & Spas'),
    ('Computers & Electronics', 'Computers & Electronics'),
    ('Construction & Contractors', 'Construction & Contractors'),
    ('Education', 'Education'),
    ('Entertainment', 'Entertainment'),
    ('Financial Services', 'Financial Services'),
    ('Fitness', 'Fitness'),
    ('Food & Dining', 'Food & Dining'),
    ('Health & Medicine', 'Health & Medicine'),
    ('Home & Garden', 'Home & Garden'),
    ('Hotels & Travel', 'Hotels & Travel'),
    ('Insurance', 'Insurance'),
    ('Legal & Financial', 'Legal & Financial'),
    ('Manufacturing', 'Manufacturing'),
    ('Media & Communications', 'Media & Communications'),
    ('Personal Care & Services', 'Personal Care & Services'),
    ('Professional Services', 'Professional Services'),
    ('Real Estate', 'Real Estate'),
    ('Shopping & Retail', 'Shopping & Retail'),
    ('Sports & Recreation', 'Sports & Recreation'),
    ('Transportation', 'Transportation'),
    ('Utilities', 'Utilities'),
    ('Wellness', 'Wellness'),
    ('Arts & Crafts', 'Arts & Crafts'),
    ('Clothing & Accessories', 'Clothing & Accessories'),
    ('Consulting', 'Consulting'),
    ('IT Services', 'IT Services'),
    ('Marketing & Advertising', 'Marketing & Advertising'),
    ('Pet Services', 'Pet Services')
]

TIME_ZONE_CHOICES = [
    ('UTC-12:00', 'International Date Line West'),
    ('UTC-11:00', 'Coordinated Universal Time-11'),
    ('UTC-10:00', 'Hawaii'),
    ('UTC-09:00', 'Alaska'),
    ('UTC-08:00', 'Pacific Time (US & Canada)'),
    ('UTC-05:00', 'Eastern Time (US & Canada)'),
    ('UTC+01:00', 'Central European Time (Berlin, Madrid, Paris)'),
    ('UTC+05:30', 'India Standard Time (New Delhi)'),
    ('UTC+08:00', 'China Standard Time (Beijing)'),
    ('UTC+09:00', 'Japan Standard Time (Tokyo)'),
    ('UTC+10:00', 'Australian Eastern Time (Sydney)'),
    ('UTC+12:00', 'New Zealand Standard Time (Auckland)')
]

DAYS_OF_WEEK_CHOICES = [
    ('Mon', 'Monday'),
    ('Tue', 'Tuesday'),
    ('Wed', 'Wednesday'),
    ('Thu', 'Thursday'),
    ('Fri', 'Friday'),
    ('Sat', 'Saturday'),
    ('Sun', 'Sunday')
]

HOUR_CHOICES = [(str(h), f'{h%12 if h != 12 and h != 0 else 12} {"AM" if h < 12 else "PM"}') for h in range(24)]
MINUTE_CHOICES = [(str(m), f'{m:02d}') for m in range(0, 60, 15)] 

