def dr_timeslots(request):
    # Check if a 'Docs' object exists for the logged-in user
    try:
        logged_in_doctor = Docs.objects.get(user=request.user)
    except Docs.DoesNotExist:
        # Handle the case where a 'Docs' object does not exist for the logged-in user
        # You can redirect or display an error message as needed
        return render(request, 'error_template.html', {'error_message': 'Doctor profile not found'})

    # Extract the doctor's name from the 'Name' attribute of the 'Docs' object
    doctor_name = logged_in_doctor.Name

    if request.method == 'POST':
        # Retrieve form data from POST request
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        if start_time:
            # Create and save the time slot associated with the logged-in doctor
            doctor = logged_in_doctor  # Use the 'logged_in_doctor' from your previous code
            slot = Slots(doctor=doctor, date=date, start_time=start_time, end_time=end_time)
            slot.save()

            # Optionally, you can add a success message or redirect to another page
            return render(request, 'dr_timeslots.html', {'doctor_name': doctor_name, 'success_message': 'Time slot saved successfully'})
        else:
            # Handle the case where 'start_time' is not provided
            # You can render an error message or take appropriate action
            return render(request, 'dr_timeslots.html', {'doctor_name': doctor_name, 'error_message': 'Please provide a valid start time'})

    # Render the template for both GET and POST requests
    return render(request, 'dr_timeslots.html', {'doctor_name': doctor_name})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Slots, Docs

@login_required
def dr_timeslots_shows(request):
    # Get the logged-in doctor
    logged_in_doctor = Docs.objects.get(user=request.user)

    # Fetch time slots associated with the logged-in doctor
    time_slots = Slots.objects.filter(doctor=logged_in_doctor)

    return render(request, 'dr_timeslots_shows.html', {'time_slots': time_slots})


def get_dates(request, doctor_id):
    try:
        # Fetch dates for the selected doctor (doctor_id) from your database
        # Replace the following line with your actual database query logic
        dates = Slots.objects.filter(doctor_id=doctor_id).values_list('date', flat=True).distinct()
        
        # Construct a list of date options in HTML format
        date_options = ["<option value='{0}'>{0}</option>".format(date.strftime('%Y-%m-%d')) for date in dates]
    except Slots.DoesNotExist:
        # Handle the case where no slots are found for the selected doctor
        date_options = []

    return JsonResponse({"date_options": date_options})

# def get_times(request, doctor_id, selected_date):
#     try:
#         # Fetch time slots for the selected doctor (doctor_id) and date (selected_date) from your database
#         # Replace the following line with your actual database query logic
#         time_slots = Slots.objects.filter(doctor_id=doctor_id, date=selected_date).values_list('start_time', 'end_time')
        
#         # Construct a list of time slot options in HTML format
#         time_options = ["<option value='{0}'>{0}</option>".format(time_slot[0].strftime('%I:%M %p') + ' - ' + time_slot[1].strftime('%I:%M %p')) for time_slot in time_slots]
#     except Slots.DoesNotExist:
#         # Handle the case where no slots are found for the selected doctor and date
#         time_options = []

#     return JsonResponse({"time_options": time_options})
from django.http import JsonResponse
from .models import Slots  # Import your Slots model or adjust the import path accordingly

from django.http import JsonResponse
from .models import Slots, Appointment

def get_times(request, doctor_id, selected_date):
    try:
        # Fetch all time slots for the selected doctor (doctor_id) and date (selected_date) from your database
        all_time_slots = Slots.objects.filter(doctor_id=doctor_id, date=selected_date)

        # Fetch the time slots that are already booked as appointments
        booked_time_slots = Appointment.objects.filter(doctor_id=doctor_id, date=selected_date).values_list('slot__id', flat=True)

        # Filter out the free time slots by excluding the booked ones
        free_time_slots = all_time_slots.exclude(id__in=booked_time_slots)

        # Construct a list of free time slot options in HTML format
        time_options = [
            {
                "id": slot.id,
                "text": f"{slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}"
            }
            for slot in free_time_slots
        ]
    except Slots.DoesNotExist:
        # Handle the case where no slots are found for the selected doctor and date
        time_options = []

    return JsonResponse({"time_options": time_options})


<body>
    <div class="navbar">
        <a href= "{% url 'profile' %}">Profiles</a>
        <a href="#appointments">Appointments</a>
        <a href= "{% url 'dr_timeslots_shows' %}">View Time Slots</a>
        <a href= "{% url 'dr_timeslots' %}">Add Time Slots</a>
        <!-- Add login and logout links here -->
    </div>
    <h1>Add Time Slots</h1>
    <div class="container">
        <form method="post">
            {% csrf_token %}
            <label for="doctor">Doctor:</label>
            <input type="text" id="doctor" value="{{ doctor_name }}" readonly>
            <label for="date">Date:</label>
            <input type="date" id="date"  name="date" required>
            <label for="start_time">Start Time:</label>
            <input type="time" id="start_time" name="start_time" required>
            <label for="end_time">End Time:</label>
            <input type="time" id="end_time"name="end_time" required>
            <button type="submit">Save</button>
        </form>
        {% if success_message %}
        <div class="success-message">{{ success_message }}</div>
        {% endif %}
    </div>
</body>
<script>
    // Get a reference to the date input field by its ID
    var reservationDateInput = document.getElementById('date');
  
    // Get today's date
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth() + 1; // January is 0
    var yyyy = today.getFullYear();
  
    // Format today's date as "YYYY-MM-DD"
    if (dd < 10) {
        dd = '0' + dd;
    }
  
    if (mm < 10) {
        mm = '0' + mm;
    }
  
    today = yyyy + '-' + mm + '-' + dd;
  
    // Set the minimum date attribute to today
    reservationDateInput.min = today;
  
    // Add an event listener for date input changes
    reservationDateInput.addEventListener('change', function () {
        var selectedDate = new Date(this.value);
        if (selectedDate < today) {
            alert('Please select a date from today onwards.');
            this.value = today; // Reset the input value to today's date
        }
    });
  </script>
  
</html>

<body>
    <div class="navbar">
        <a href= "{% url 'profile' %}">Profiles</a>
        <a href="#appointments">Appointments</a>
        <a href= "{% url 'dr_timeslots_shows' %}">View Time Slots</a>
        <a href= "{% url 'dr_timeslots' %}">Add Time Slots</a>
        <!-- Add login and logout links here -->
    </div>
    <h1>My Time Slots</h1>
    
    <ul>
        {% for slot in time_slots %}
            <li>
                <div>
                    <strong>Date:</strong> {{ slot.date }}<br>
                    <strong>Time:</strong> {{ slot.start_time }} to {{ slot.end_time }}
                </div>
                <div>
                    <!-- Add additional information here if needed -->
                </div>
            </li>
        {% empty %}
            <li class="no-slots">No time slots available.</li>
        {% endfor %}
    </ul>

    <!-- Add additional content or styling as needed -->
</body>


class Slots(models.Model):
    doctor = models.ForeignKey(Docs, on_delete=models.CASCADE)
    date = models.DateField(null=True,blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    def _str_(self):
        return f"Slot for Dr. {self.doctor.Name} on {self.date} at {self.start_time}-{self.end_time}"

class Appointment(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    place = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others')], blank=True, null=True)
    mobile = models.CharField(max_length=15)
    allergy = models.CharField(max_length=3)
    reason = models.TextField()
    doctor = models.ForeignKey(Docs, on_delete=models.CASCADE, related_name='appointments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    slot = models.ForeignKey(Slots, on_delete=models.CASCADE)
    date = models.DateField()
    status=models.BooleanField(default=True)