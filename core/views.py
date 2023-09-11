from django.shortcuts import redirect, render


def home(request):
    # return render(
    #     request=request,
    #     template_name="base.html"
    # )
    return redirect(to='login')


def error_404(request, exception):
    """Manejo de error 404"""
    return render(
        request=request,
        template_name="404.html"
    )


def error_500(request):
    """Manejo de error 500"""
    return render(
        request=request,
        template_name="500.html"
    )


def redirect_to_rg276(request):
    rg_url = 'https://docs.google.com/spreadsheets/d/1KWKclWl7WEMrBtRlaLoCBd4wGknXB8LlHwRPfn6yvo4'
    return redirect(to=rg_url)
