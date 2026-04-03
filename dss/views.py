from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.views.generic import TemplateView
from django.db.models import Count, Avg, Func
from django.db.models.functions import ExtractYear
from .models import SateliteAnomaly, DSSCore
from .forms import DssModelForm
from django.http import JsonResponse
import logging
import requests
import json
import markdown
import datetime

#from reportlab.pdfgen import canvas

#from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.units import inch
from reportlab.lib import colors
from django.http import HttpResponse

"""
import joblib


"""

class Index(TemplateView):
    template_name = 'dss/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_altitude'] = SateliteAnomaly.objects.filter(event__startswith='Attitude').aggregate(total_altitude=Count('sa_id'))['total_altitude']
        context['total_beam'] = SateliteAnomaly.objects.filter(event__startswith='Beam').aggregate(total_beam=Count('sa_id'))['total_beam']
        context['total_control'] = SateliteAnomaly.objects.filter(event__startswith='Control').aggregate(total_control=Count('sa_id'))['total_control']
        context['total_docking'] = SateliteAnomaly.objects.filter(event__startswith='Docking').aggregate(total_docking=Count('sa_id'))['total_docking']
        context['total_mechanism'] = SateliteAnomaly.objects.filter(event__startswith='Mechanisms').aggregate(total_mechanism=Count('sa_id'))['total_mechanism']
        context['total_payload'] = SateliteAnomaly.objects.filter(event__startswith='Payload').aggregate(total_payload=Count('sa_id'))['total_payload']
        context['total_battery'] = SateliteAnomaly.objects.filter(event__startswith='Power - Battery').aggregate(total_battery=Count('sa_id'))['total_battery']
        context['total_electrical'] = SateliteAnomaly.objects.filter(event__startswith='Power - Electrical').aggregate(total_electrical=Count('sa_id'))['total_electrical']
        context['total_solar'] = SateliteAnomaly.objects.filter(event__startswith='Power - Solar').aggregate(total_solar=Count('sa_id'))['total_solar']
        context['total_telemetry'] = SateliteAnomaly.objects.filter(event__startswith='Telemetry').aggregate(total_telemetry=Count('sa_id'))['total_telemetry']
        context['total_transponder'] = SateliteAnomaly.objects.filter(event__startswith='Transponder').aggregate(total_transponder=Count('sa_id'))['total_transponder']
        context['total_unknown'] = SateliteAnomaly.objects.filter(event__startswith='Unknown').aggregate(total_unknown=Count('sa_id'))['total_unknown']
        
        # Custom function to extract the first word from the event field
        class FirstWord(Func):
            function = 'split_part'
            template = "%(function)s(%(expressions)s, ' ', 1)"

        anomalies_by_event = SateliteAnomaly.objects.annotate(first_word=FirstWord('event')).values('first_word').annotate(total=Count('sa_id')).order_by('first_word')
        context['anomalies_by_event'] = list(anomalies_by_event)


        anomalies_by_mission = SateliteAnomaly.objects.annotate(mission=FirstWord('missionprimary')).values('mission').annotate(total=Count('sa_id')).order_by('mission')
        context['anomalies_by_mission'] = list(anomalies_by_mission)

        anomalies_by_year = SateliteAnomaly.objects.values(year=ExtractYear('eventdate')).annotate(total=Count('sa_id')).order_by('year')
        context['anomalies_by_year'] = list(anomalies_by_year)
        print(anomalies_by_year)

        anomalies_by_orbit = SateliteAnomaly.objects.values('orbitcategory').annotate(total=Count('sa_id')).order_by('orbitcategory')
        context['anomalies_by_orbit'] = list(anomalies_by_orbit)
        
        designlife_by_orbit = SateliteAnomaly.objects.values('orbitcategory').annotate(avg_dl=Avg('designlife')).order_by('orbitcategory')
        # Replace None values with 0 in the query result for designlife_by_orbit
        for item in designlife_by_orbit:
            if item['avg_dl'] is None:
                item['avg_dl'] = 0
        context['designlife_by_orbit'] = list(designlife_by_orbit)

        age_by_orbit = SateliteAnomaly.objects.values('orbitcategory').annotate(avg_age=Avg('age')).order_by('orbitcategory')
        # Replace None values with 0 in the query result for designlife_by_orbit
        for item in age_by_orbit:
            if item['avg_age'] is None:
                item['avg_age'] = 0
        context['age_by_orbit'] = list(age_by_orbit)
        
        anomalies_by_manufacturer = SateliteAnomaly.objects.values('primemanufacturer').annotate(total=Count('sa_id')).order_by('-total')[:10]
        context['anomalies_by_manufacturer'] = list(anomalies_by_manufacturer)
        
        anomalies_by_operator = SateliteAnomaly.objects.values('spacecraftoperator').annotate(total=Count('sa_id')).order_by('-total')[:10]
        context['anomalies_by_operator'] = list(anomalies_by_operator)
        
        return context


def user_login(request):
    if request.method == "POST":
        username = requests.POST['username']
        password = requests.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect ('index')
        else:
            messages.success(request, ("Username or Password is incorrect"))    
    return render(request, 'dss/login.html')

def user_logout(request):
    logout(request)
    return redirect ('index')
    
#class Loginuser(TemplateView):
#    template_name = 'dss/login.html'

class AnomData(TemplateView):
    template_name = 'dss/anomdata.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['satellite_anomaly'] = SateliteAnomaly.objects.all()
        return context

def autocomplete_bustype(request):
    if 'term' in request.GET:
        term = request.GET.get('term')
        bustypes = SateliteAnomaly.objects.filter(bustype__icontains=term).values_list('bustype', flat=True).distinct().order_by('bustype')
        return JsonResponse(list(bustypes), safe=False)        

def autocomplete_missionprimary(request):
    if 'term' in request.GET:
        term = request.GET.get('term')
        missionprimary = SateliteAnomaly.objects.filter(missionprimary__icontains=term).values_list('missionprimary', flat=True).distinct().order_by('missionprimary')
        return JsonResponse(list(missionprimary), safe=False)

class DSupport(TemplateView):
    template_name = 'dss/analysis.html'
    """model = joblib.load('model/klz-model.pkl')"""

    def post(self, request, *args, **kwargs):
        bustype = request.POST.get('bustype')
        orbitcategory = request.POST.get('orbitcategory')
        missionprimary = request.POST.get('missionprimary')
        genai = request.POST.get('genai')
        analysis_content = ""
        overview=""
        insight=""
        recommendation=""
        summary=""
        logging.info(f"post data = { bustype } -  { orbitcategory }  -  { missionprimary }")

        filter_params = {}
        if bustype:
            filter_params['bustype'] = bustype
        if orbitcategory:
            filter_params['orbitcategory'] = orbitcategory
        if missionprimary:
            filter_params['missionprimary'] = missionprimary

        results = SateliteAnomaly.objects.filter(**filter_params)

        if results:
            # Convert QuerySet to a list of dictionaries
            results_list = list(results.values())

            # Execute the raw query
            resultsgai = DSSCore.objects.filter(
                bustype=bustype,
                orbitcategory=orbitcategory,
                missionprimary=missionprimary,
                genai=genai
            )


            for record in resultsgai:
                overview = record.incident_overview
                insight = record.reliability_insight
                recommendation = record.recommendation
                summary = record.summary

            #print("query resultsgai ")
            #print(recommendation)

            if not resultsgai:
                if genai == "MetaAI":
                    response1 = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": "Bearer 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", # Meta: Llama 4
                            "Content-Type": "application/json",
                            "HTTP-Referer": "", # Optional. Site URL for rankings on openrouter.ai.
                            "X-Title": "TestAI", # Optional. Site title for rankings on openrouter.ai.
                        },
                        data=json.dumps({
                            #"model": "deepseek/deepseek-r1:free",
                            "model": "meta-llama/llama-4-maverick:free",
                            "messages": [
                              {
                                "role": "user",
                                "content": f"As an expert in satellite area, write the incident overview related to mission primary, orbit category, mass at launch, age and design life especially for age less than design life based on the data as provided. \n {results_list}"
                              }
                            ],
                            
                        })

                    )

                    response2 = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": "Bearer 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", # Meta: Llama 4
                            "Content-Type": "application/json",
                            "HTTP-Referer": "", # Optional. Site URL for rankings on openrouter.ai.
                            "X-Title": "TestAI", # Optional. Site title for rankings on openrouter.ai.
                        },
                        data=json.dumps({
                            "model": "meta-llama/llama-4-maverick:free",
                            "messages": [
                              {
                                "role": "user",
                                "content": f"As an expert in satellite area, write the Reliability Trends & Insights related to mission primary, orbit category, mass at launch, age and design life especially for age less than design life based on the data as provided. \n {results_list}"
                              }
                            ],
                            
                        })

                    )

                    response3 = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": "Bearer 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", # Meta: Llama 4
                            "Content-Type": "application/json",
                            "HTTP-Referer": "", # Optional. Site URL for rankings on openrouter.ai.
                            "X-Title": "TestAI", # Optional. Site title for rankings on openrouter.ai.
                        },
                        data=json.dumps({
                            "model": "meta-llama/llama-4-maverick:free",
                            "messages": [
                              {
                                "role": "user",
                                "content": f"As an expert in satellite area, write the Stakeholder Recommendations related to mission primary, orbit category, mass at launch, age and design life especially for age less than design life based on the data as provided. \n {results_list}"
                              }
                            ],
                            
                        })

                    )

                    response4 = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": "Bearer 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", # Meta: Llama 4
                            "Content-Type": "application/json",
                            "HTTP-Referer": "", # Optional. Site URL for rankings on openrouter.ai.
                            "X-Title": "TestAI", # Optional. Site title for rankings on openrouter.ai.
                        },
                        data=json.dumps({
                            "model": "meta-llama/llama-4-maverick:free",
                            "messages": [
                              {
                                "role": "user",
                                "content": f"As an expert in satellite area, write the summary regarding the following analysis: \n {response1} \n {response2} \n {response3}"
                              }
                            ],
                            
                        })

                    )

                elif genai == "NVIDIA":
                    response1 = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": "Bearer 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",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "", # Optional. Site URL for rankings on openrouter.ai.
                            "X-Title": "TestAI", # Optional. Site title for rankings on openrouter.ai.
                        },
                        data=json.dumps({
                            "model": "nvidia/nemotron-nano-9b-v2:free",
                            "messages": [
                              {
                                "role": "user",
                                "content": f"As an expert in satellite area, write the incident overview related to mission primary, orbit category, mass at launch, age and design life especially for age less than design life based on the data as provided. \n {results_list}"
                              }
                            ],
                            
                        })

                    )

                    response2 = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": "Bearer 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",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "", # Optional. Site URL for rankings on openrouter.ai.
                            "X-Title": "TestAI", # Optional. Site title for rankings on openrouter.ai.
                        },
                        data=json.dumps({
                            "model": "nvidia/nemotron-nano-9b-v2:free",
                            "messages": [
                              {
                                "role": "user",
                                "content": f"As an expert in satellite area, write the Reliability Trends & Insights related to mission primary, orbit category, mass at launch, age and design life especially for age less than design life based on the data as provided. \n {results_list}"
                              }
                            ],
                            
                        })

                    )

                    response3 = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": "Bearer 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",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "", # Optional. Site URL for rankings on openrouter.ai.
                            "X-Title": "TestAI", # Optional. Site title for rankings on openrouter.ai.
                        },
                        data=json.dumps({
                            "model": "nvidia/nemotron-nano-9b-v2:free",
                            "messages": [
                              {
                                "role": "user",
                                "content": f"As an expert in satellite area, write the Stakeholder Recommendations related to mission primary, orbit category, mass at launch, age and design life especially for age less than design life based on the data as provided. \n {results_list}"
                              }
                            ],
                            
                        })

                    )

                    response4 = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            #"Authorization": "Bearer sk-or-v1-ffc9be79280f59a7b41d28914cf5109se50ec1fb30cad79b0b610797ef4fb413b", # NVIDIA: Llama 3.1 Nemotron
                            "Authorization": "Bearer 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",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "", # Optional. Site URL for rankings on openrouter.ai.
                            "X-Title": "TestAI", # Optional. Site title for rankings on openrouter.ai.
                        },
                        data=json.dumps({
                            #"model": "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
                            "model": "nvidia/nemotron-nano-9b-v2:free",
                            "messages": [
                              {
                                "role": "user",
                                "content": f"As an expert in satellite area, write the summary regarding the following analysis: \n {response1} \n {response2} \n {response3}"
                              }
                            ],
                            
                        })

                    )

                elif genai == "Gemini":
                    response1 = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            #"Authorization": "Bearer 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", # Google: Gemini 2.0 Flash Experimental (free)
                            "Authorization": "Bearer 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", #google gemma
                            "Content-Type": "application/json",
                            "HTTP-Referer": "", # Optional. Site URL for rankings on openrouter.ai.
                            "X-Title": "TestAI", # Optional. Site title for rankings on openrouter.ai.
                        },
                        data=json.dumps({
                            #"model": "google/gemini-2.0-flash-exp:free",
                            "model": "google/gemma-3-27b-it:free",
                            "messages": [
                              {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"As an expert in satellite area, write the incident overview related to mission primary, orbit category, mass at launch, age and design life especially for age less than design life based on the data as provided. \n {results_list}"
                                    }
                                ]
                              }
                            ],
                            
                        })

                    )

                    response2 = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            #"Authorization": "Bearer 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", # Google: Gemini 2.0 Flash Experimental (free)
                            "Authorization": "Bearer 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", #google gemma
                            "Content-Type": "application/json",
                            "HTTP-Referer": "", # Optional. Site URL for rankings on openrouter.ai.
                            "X-Title": "TestAI", # Optional. Site title for rankings on openrouter.ai.
                        },
                        data=json.dumps({
                            #"model": "google/gemini-2.0-flash-exp:free",
                            "model": "google/gemma-3-27b-it:free",
                            "messages": [
                              {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"As an expert in satellite area, write the Reliability Trends & Insights related to mission primary, orbit category, mass at launch, age and design life especially for age less than design life based on the data as provided. \n {results_list}"
                                    }
                                ]
                              }
                            ],
                            
                        })

                    )

                    response3 = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            #"Authorization": "Bearer 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", # Google: Gemini 2.0 Flash Experimental (free)
                            "Authorization": "Bearer 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", #google gemma
                            "Content-Type": "application/json",
                            "HTTP-Referer": "", # Optional. Site URL for rankings on openrouter.ai.
                            "X-Title": "TestAI", # Optional. Site title for rankings on openrouter.ai.
                        },
                        data=json.dumps({
                            #"model": "google/gemini-2.0-flash-exp:free",
                            "model": "google/gemma-3-27b-it:free",
                            "messages": [
                              {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"As an expert in satellite area, write the Stakeholder Recommendations related to mission primary, orbit category, mass at launch, age and design life especially for age less than design life based on the data as provided. \n {results_list}"
                                    }
                                ]
                              }
                            ],
                            
                        })

                    )

                    response4 = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            #"Authorization": "Bearer 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", # Google: Gemini 2.0 Flash Experimental (free)
                            "Authorization": "Bearer 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", #google gemma
                            "Content-Type": "application/json",
                            "HTTP-Referer": "", # Optional. Site URL for rankings on openrouter.ai.
                            "X-Title": "TestAI", # Optional. Site title for rankings on openrouter.ai.
                        },
                        data=json.dumps({
                            #"model": "google/gemini-2.0-flash-exp:free",
                            "model": "google/gemma-3-27b-it:free",
                            "messages": [
                              {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"As an expert in satellite area, write the summary regarding the following analysis: \n {response1} \n {response2} \n {response3}"
                                    }
                                ]
                              }
                            ],
                            
                        })

                    )
                
                elif genai == "Mistral":
                    response1 = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": "Bearer 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", # Mistral: Devstral Small
                            "Content-Type": "application/json",
                            "HTTP-Referer": "", # Optional. Site URL for rankings on openrouter.ai.
                            "X-Title": "TestAI", # Optional. Site title for rankings on openrouter.ai.
                        },
                        data=json.dumps({
                            "model": "mistralai/devstral-small-2505:free",
                            "messages": [
                              {
                                "role": "user",
                                "content": f"As an expert in satellite area, write the incident overview related to mission primary, orbit category, mass at launch, age and design life especially for age less than design life based on the data as provided. \n {results_list}"
                              }
                            ],
                            
                        })

                    )

                    response2 = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": "Bearer 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", # Mistral: Devstral Small
                            "Content-Type": "application/json",
                            "HTTP-Referer": "", # Optional. Site URL for rankings on openrouter.ai.
                            "X-Title": "TestAI", # Optional. Site title for rankings on openrouter.ai.
                        },
                        data=json.dumps({
                            "model": "mistralai/devstral-small-2505:free",
                            "messages": [
                              {
                                "role": "user",
                                "content": f"As an expert in satellite area, write the Reliability Trends & Insights related to mission primary, orbit category, mass at launch, age and design life especially for age less than design life based on the data as provided. \n {results_list}"
                              }
                            ],
                            
                        })

                    )

                    response3 = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": "Bearer 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", # Mistral: Devstral Small
                            "Content-Type": "application/json",
                            "HTTP-Referer": "", # Optional. Site URL for rankings on openrouter.ai.
                            "X-Title": "TestAI", # Optional. Site title for rankings on openrouter.ai.
                        },
                        data=json.dumps({
                            "model": "mistralai/devstral-small-2505:free",
                            "messages": [
                              {
                                "role": "user",
                                "content": f"As an expert in satellite area, write the Stakeholder Recommendations related to mission primary, orbit category, mass at launch, age and design life especially for age less than design life based on the data as provided. \n {results_list}"
                              }
                            ],
                            
                        })

                    )

                    response4 = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": "Bearer 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", # Mistral: Devstral Small
                            "Content-Type": "application/json",
                            "HTTP-Referer": "", # Optional. Site URL for rankings on openrouter.ai.
                            "X-Title": "TestAI", # Optional. Site title for rankings on openrouter.ai.
                        },
                        data=json.dumps({
                            #"model": "mistralai/devstral-small:free",
                            "model": "mistralai/devstral-small-2505:free",
                            "messages": [
                              {
                                "role": "user",
                                "content": f"As an expert in satellite area, write the summary regarding the following analysis: \n {response1} \n {response2} \n {response3}"
                              }
                            ],
                            
                        })

                    )
                ## Check the response status code
                logging.info(f"Response status code: {response1.status_code}")

                # Log the raw response content
                logging.info(f"Raw response content: {response1.text}")

                # Parse the JSON response
                try:
                    dataanalysis1 = response1.json()
                    logging.info(f"API response 1: {dataanalysis1}")

                    markdown_text1 = dataanalysis1.get('choices', [{}])[0].get('message', {}).get('content', 'No response received.')
                    logging.info(f"Extracted content 1: {markdown_text1}")

                    # Convert Markdown to HTML using the markdown library
                    analysis_content1 = markdown.markdown(markdown_text1)

                    dataanalysis2 = response2.json()
                    logging.info(f"API response 2: {dataanalysis1}")

                    markdown_text2 = dataanalysis2.get('choices', [{}])[0].get('message', {}).get('content', 'No response received.')
                    logging.info(f"Extracted content 2: {markdown_text2}")

                    # Convert Markdown to HTML using the markdown library
                    analysis_content2 = markdown.markdown(markdown_text2)

                    dataanalysis3 = response3.json()
                    logging.info(f"API response 3: {dataanalysis1}")

                    markdown_text3 = dataanalysis3.get('choices', [{}])[0].get('message', {}).get('content', 'No response received.')
                    logging.info(f"Extracted content 3: {markdown_text3}")

                    # Convert Markdown to HTML using the markdown library
                    analysis_content3 = markdown.markdown(markdown_text3)

                    dataanalysis4 = response4.json()
                    logging.info(f"API response 4: {dataanalysis1}")

                    markdown_text4 = dataanalysis1.get('choices', [{}])[0].get('message', {}).get('content', 'No response received.')
                    logging.info(f"Extracted content 4: {markdown_text4}")

                    # Convert Markdown to HTML using the markdown library
                    analysis_content4 = markdown.markdown(markdown_text4)


                    # Create a new record
                    new_data = DSSCore(
                        bustype             = bustype,
                        orbitcategory       = orbitcategory,
                        missionprimary      = missionprimary,
                        genai               = genai,
                        incident_overview   = analysis_content1,
                        reliability_insight = analysis_content2,
                        recommendation      = analysis_content3,
                        summary             = analysis_content4
                    )
                    new_data.save()

                    overview       = analysis_content1
                    insight        = analysis_content2
                    recommendation = analysis_content3
                    summary        = analysis_content4

                except json.JSONDecodeError as e:
                    logging.error(f"JSON decode error: {e}")
                    markdown_text1 = 'Error decoding JSON response.'


        context = {
            'bustype': bustype,
            'orbitcategory': orbitcategory,
            'missionprimary': missionprimary,
            'genai': genai,
            'results': results,
            'overview': overview,
            'insight': insight,
            'recommendation': recommendation,
            'summary': summary
        }

        return render(request, self.template_name, context)


import re
def generate_pdf(request):
    # Get the filter parameters from the request
    bustype = request.GET.get('bustype')
    orbitcategory = request.GET.get('orbitcategory')
    missionprimary = request.GET.get('missionprimary')

    # Create a PDF document
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="output.pdf"'
    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    title = Paragraph("Analysis Report", ParagraphStyle('Title', parent=styles['Title'], alignment=1))
    story.append(title)
    story.append(Spacer(1, 0.5 * inch)) # Add some space after the title

    # Query the DSSCore objects
    result = DSSCore.objects.filter(
        bustype=bustype,
        orbitcategory=orbitcategory,
        missionprimary=missionprimary
    )

    # Function to add breaks before <strong> tags
    def add_breaks_before_strong(text):
        return re.sub(r'(<strong>)', r'<br/><br/>\1', text)

    # Iterate through the result and add the data to the PDF
    for record in result:
        story.append(Paragraph(add_breaks_before_strong(record.incident_overview), styles['Normal']))
        story.append(Spacer(1, 12)) # Add some space between records
        story.append(HRFlowable(width="100%", thickness=1, color=colors.black)) # Add a horizontal line between paragraphs
        story.append(Paragraph(add_breaks_before_strong(record.reliability_insight), styles['Normal']))
        story.append(Spacer(1, 12)) # Add some space between records
        story.append(HRFlowable(width="100%", thickness=1, color=colors.black)) # Add a horizontal line between paragraphs
        story.append(Paragraph(add_breaks_before_strong(record.recommendation), styles['Normal']))
        story.append(Spacer(1, 12)) # Add some space between records
        story.append(HRFlowable(width="100%", thickness=1, color=colors.black)) # Add a horizontal line between paragraphs
        story.append(Paragraph(add_breaks_before_strong(record.summary), styles['Normal']))
        story.append(Spacer(1, 12)) # Add some space between records
        

    # Build the PDF
    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)

    return response

def add_header_footer(canvas, doc):
    # Add header
    canvas.saveState()
    canvas.setFont('Helvetica-Oblique', 10)
    canvas.drawString(40, A4[1] - 20, "ANTspace@2025 ::-:: Powered by AOARD")
    

    # Add footer
    canvas.drawString(40, 20, f"Printed on {datetime.datetime.now().strftime('%Y-%m-%d')}")

    #Add page number
    canvas.drawRightString(A4[0] - 40, 20, f"Page {doc.page}")
    canvas.restoreState()


