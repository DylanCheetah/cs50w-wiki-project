import random

from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render

import markdown2

from . import util


class CreatePageForm(forms.Form):
    title = forms.CharField(label="Title")
    markdown = forms.CharField(label="Markdown", widget=forms.Textarea(attrs={"rows": 8}))


class EditPageForm(forms.Form):
    markdown = forms.CharField(label="Markdown", widget=forms.Textarea(attrs={"rows": 8}))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def wiki(request, title):
    # Try to get the requested wiki entry
    entry = util.get_entry(title)

    # Display the wiki entry or an error page
    if entry is not None:
        return render(request, "encyclopedia/wiki.html", {
            "title": title,
            "entry": markdown2.markdown(entry)
        })
    
    else:
        return render(request, "encyclopedia/error.html", {
            "error_msg": f"No entry with the title '{title}' could be found."
        })
    

def search(request):
    # Get the search query and the list of wiki entries
    query = request.GET["q"]
    entries = util.list_entries()

    # If there was an exact match, redirect to the page for the requested entry
    if query in entries:
        return HttpResponseRedirect(reverse("wiki", args=[query]))
    
    # Otherwise, we will display all wiki entries with a title similar to the query
    results = [entry for entry in entries if query in entry]
    return render(request, "encyclopedia/search.html", {
        "results": results
    })
    

def create_page(request):
    # Handle submitted form data
    if request.method == "POST":
        # Validate form data
        form = CreatePageForm(request.POST)

        if form.is_valid():
            # Fetch form data
            title = form.cleaned_data["title"]
            markdown = form.cleaned_data["markdown"]

            # Does a page with the given title already exist?
            if title in util.list_entries():
                # Redisplay the form with an alert
                return render(request, "encyclopedia/create-page.html", {
                    "duplicate_title": True,
                    "form": form
                })
            
            # Create the new wiki page and redirect to it
            util.save_entry(title, markdown)
            return HttpResponseRedirect(reverse("wiki", args=[title]))

        else:
            # Redisplay the form
            return render(request, "encyclopedia/create-page.html", {
                "form": form
            })

    # Display the form for creating a new wiki page
    return render(request, "encyclopedia/create-page.html", {
        "form": CreatePageForm()
    })


def edit_page(request, title):
    # Handle submitted form data
    if request.method == "POST":
        # Validate the form
        form = EditPageForm(request.POST)

        if form.is_valid():
            # Save changes to the page and redirect back to the page
            util.save_entry(title, form.cleaned_data["markdown"])
            return HttpResponseRedirect(reverse("wiki", args=[title]))

        else:
            # Redisplay the form
            return render(request, "encyclopedia/edit-page.html", {
                "title": title,
                "form": form
            })

    # Get the markdown for the given entry
    markdown = util.get_entry(title)
    markdown = markdown.replace("\r\n", "\n") # BUGFIX: On Windows, we need to convert the line endings

    # Redirect to the new page form if the page doesn't exist
    if markdown is None:
        return HttpResponseRedirect(reverse("create-page"))

    # Display the edit page form
    return render(request, "encyclopedia/edit-page.html", {
        "title": title,
        "form": EditPageForm({"markdown": markdown})
    })


def random_page(request):
    # Choose a random wiki entry and redirect to it
    title = random.choice(util.list_entries())
    return HttpResponseRedirect(reverse("wiki", args=[title]))
