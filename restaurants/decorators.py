from django.shortcuts import redirect

def restaurant_user_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.groups.filter(name='Restaurant User').exists():
            return view_func(request, *args, **kwargs)
        else:
            return redirect('/home/unauthorized')  # Redirect or handle unauthorized access as needed
    return wrapper