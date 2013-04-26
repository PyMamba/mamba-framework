{% extends "layout.html" %}
    {% block content %}
    {{ super() }}

    <!--
        Copyright (c) ${year} - ${author} <${author_email}>

        view: ${view_name}
            synopsis: ${synopsis}

        viewauthor: ${author} <${author_email}>
    -->

    <h2>It works!</h2>

    {% endblock %}
