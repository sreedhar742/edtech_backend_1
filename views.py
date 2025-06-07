from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
# from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from .models import classes, Subject, Topics, SubTopics 
from rest_framework.permissions import IsAuthenticated
import pandas as pd
from django.db import IntegrityError
# from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from .models import classes, Subject, Topics, SubTopics, Question_Answers
from .serializers import ChapterSerializer, ClassSerializer, SubjectSerializer, TopicSerializer, SubTopicSerializer, InputSerializer
from Users.models import Student
import json
import requests

class ChapterListCreateView(generics.ListCreateAPIView):
    queryset = Topics.objects.all()
    serializer_class = ChapterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            "status": "Success",
            "message": "Chapter(s) created successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)


class ClassListView(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        user=Student.objects.get(id=request.user.id)
        class_obj = classes.objects.filter(class_name=request.user.class_name)
        serializer = ClassSerializer(class_obj, many=True)
        return Response({
            "status": "Success",
            "message": "Classes retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class SubjectListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            subjects = Subject.objects.filter(class_name=request.user.class_name)
            serializer = SubjectSerializer(subjects, many=True)
            return Response({
                "status": "Success",
                "message": "Subjects retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Subject.DoesNotExist:
            return Response({
                "status": "Error",
                "message": "Class not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
class TopicListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, subject_id):
        try:
            topics = Topics.objects.filter(subject__id=subject_id)
            serializer = TopicSerializer(topics, many=True)
            return Response({
                "status": "Success",
                "message": "Topics and subtopics retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Topics.DoesNotExist:
            return Response({
                "status": "Error",
                "message": "Class not found."
            }, status=status.HTTP_404_NOT_FOUND)
     
class SubTopicListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, topic_id):
        try:
            subtopics = SubTopics.objects.filter(topic__id=topic_id)
            
            serializer = SubTopicSerializer(subtopics, many=True)
            return Response({
                "status": "Success",
                "message": "SubTopics retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except SubTopics.DoesNotExist:
            return Response({
                "status": "Error",
                "message": "Class not found."
            }, status=status.HTTP_404_NOT_FOUND)
#=======================--------------AI Model APIS----------============================


class QuestionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def ai_generated_questions(class_num, chapter_nums):
        url = "http://ipaddress/url/"
        data = {
            "class_num":class_num,
            "chapter_nums":chapter_nums
        }
        response = requests.post(url,data)
        if response.status_code == 200:
            questions_list = [item['question'] for item in response['json_data']['questions']]
            return questions_list
        else:
            return Response({'error': 'Failed to retrieve data from external API'}, status=response.status_code)
    def post(self, request, *args, **kwargs):
        serializer = InputSerializer(data=request.data)
        if serializer.is_valid():
            classid = serializer.validated_data['classid']
            subjectid = serializer.validated_data['subjectid']
            topicids = serializer.validated_data['topicid']
            subtopicids = serializer.validated_data['subtopicid']
            solved = serializer.validated_data.get('solved', None)
            exercise = serializer.validated_data.get('exercise', None)
            level = serializer.validated_data.get('external', None)
            
            class_name = classes.objects.get(id=classid).class_name
            # subjectname = Subject.objects.get(id=subjectid).name
            if not Topics.objects.filter(subject_id=subjectid, id__in=topicids).exists():
                return Response({"error": "Invalid topic IDs for the given subject ID."}, status=status.HTTP_400_BAD_REQUEST)
        

            # topics = Topics.objects.filter(id__in=topicids, subject_id=subjectid)
            # topic_names = list(topics.values_list('name', flat=True))  # Get list of topic names
            # number, topic_name = [name.split(',', 1) for name in topic_names]

            # # Strip any extra spaces around the topic_name
            # number = number.strip()
            # topic_name = topic_name.strip()

            # Query the topics and process names in one step
            topic_nums = [
                name.split(',', 1)[0].strip()
                for name in Topics.objects.filter(id__in=topicids, subject_id=subjectid)
                                        .values_list('name', flat=True)
            ]

            
            
            
            ai_questions = [
                        "1. Find the radian measure of an angle subtended by an arc of length 5 units in a circle of radius 2 units.",
                        "2. Convert 120° into radian measure.",
                        "3. Solve for x: cos(2x) = sin(x).",
                        "4. Determine the value of sin(75°).",
                        "5. Calculate the radius of a circle in which a central angle of 45° intercepts an arc of length 10 cm.",
                        "6. Prove that cos^2(x) + sin^2(x) = 1.",
                        "7. Find the value of tan(15°).",
                        "8. Solve for x: 2cos^2(x) + 3sin(x) = 0.",
                        "9. Prove that sin(2x) - sin(4x) + sin(6x) = 0.",
                        "10. Determine the radius of a circle if an arc of length 3 units subtends an angle of 2 radians at the center."
                    ]

            if subtopicids:
                subtopics = SubTopics.objects.filter(id__in=subtopicids, topic__id__in=topic_nums)
                subtopic_names = list(subtopics.values_list('name', flat=True))  # Get list of subtopic names


                # ai_questions = self.ai_generated_questions(int(class_name), topicids)
                

                return Response({"message": "AI-generated questions created with subtopics.", "questions":ai_questions}, status=status.HTTP_200_OK)
            else:
                
                # ai_questions= self.ai_generated_questions(int(class_name), topic_nums)
                return Response({"message": "AI-generated questions created without subtopics.","questions":ai_questions}, status=status.HTTP_200_OK)
                    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnswerSubmit(APIView):
    permission_classes = [IsAuthenticated]
    
    
    # def Ai_validation():
    #     pass
    def Ai_Explaination_step_by_step(class_nums, question):
        url = "https://ipaddress/generate-step-by-step-solution/"
        data = {"class_nums": [10], "question":question}
        response = requests.post(url,data)

        if response.status_code == 200:
            return response['Response']['step_by_step_solution']
        else:
            return Response({'error': 'Failed to retrieve data from external API'}, status=response.status_code)

    def Ai_jpg_to_text_converter(class_num, chapter_nums):
        url = "https://ipaddress/generate-questions-external"
        data = {"class_num": class_num, "chapter_nums": chapter_nums}
        response = requests.post(url,data)
        if response.status_code == 200:
            return response
        else:
            return Response({'error': 'Failed to retrieve data from external API'}, status=response.status_code)

    # def Ai_validation():
    #     pass
    

    def post(self, request, *args, **kwargs):
        # post_data = json.loads(request.body)
        class_id = request.POST.get('class_id')
        subject_id = request.POST.get('subject_id')
        question = request.POST.get('question')
        
        # topic_ids = request.POST.getlist('topic_ids')  # Get a list of topic IDs for ManyToMany
        subtopic = request.POST.get('subtopic')
        submit = request.POST.get('submit')
        solve = request.POST.get('solve')
        correct = request.POST.get('correct')
        explain = request.POST.get('explain')
        
        ans_image = request.FILES.get('ans_img')
        # Retrieve the class and subject objects
        class_obj = classes.objects.get(id=class_id)
        subject_obj = Subject.objects.get(id=subject_id)


        topic_ids_str = request.POST.get('topic_ids')  # This may come as a comma-separated string

        if topic_ids_str:
            topic_ids = [int(tid) for tid in topic_ids_str.split(',')]        # Ensure all required fields are present
        
        # Create the Question_Answers object (without adding topics yet)
        question_answer = Question_Answers.objects.create(
            user=request.user,
            question_text=question
        )

        # Add topics to the Question_Answers instance
        if topic_ids:
            topics = Topics.objects.filter(id__in=topic_ids)  # Get all topics by IDs
            question_answer.topic.add(*topics)
            processed_topics = [
                (name.split(',', 1)[0].strip())
                for name in topics.values_list('name', flat=True)
            ]

        if subtopic:
            subtopic = SubTopics.objects.get(id=subtopic)
            question_answer.subtopic=subtopic
        

        # Save the object after adding topics
        question_answer.save()

        # return Response({"success": "Question and answer created successfully"}, status=status.HTTP_201_CREATED)

        #==========---------------AI Validation Function----------===========
        data={}
        

        if submit=='true':
            
            question = "1. Find the radian measure of an angle subtended by an arc of length 5 units in a circle of radius 2 units."
            student_answer = "Find the radian measure of an angle subtended by an arc of length 5 units in a circle with a radius of 2 units. To solve this, you can use the formula: Angle (in radians) = Arc length / Radius. In this case: The arc length is 5 units. The radius is 2 units. Using the formula: Angle = 5 / 2 = 2.5 radians. Thus, the angle subtended by the arc is 2.5 radians."
            data['question'] = question
            data['student_answer'] = student_answer
            data['question_marks'] = 3
            data['obtained_marks'] = 0
            data['total_marks'] = 30
            data['key'] = 'submit'

            question_answer.ai_submit = True
            question_answer.solved = True
            question_answer.student_answer = student_answer
            question_answer.question_marks = 3
            question_answer.ai_given_marks = 2
            question_answer.total_marks = 30
            question_answer.save()
            
            # send image 
            self.Ai_jpg_to_text_converter(int(class_obj), processed_topics)
        elif correct=='true':
            # correct the answer Auto Score
            
            {'score': 8, 
             'comment': 'Good understanding of the fundamental trigonometric identity, but missing some key steps.', 
             'concepts_used': ['Trigonometric identity: sin^2 x + cos^2 x = 1'], 
             'student_answer_replication': 'sin^2 x + cos^2 x = 1', 
             'correct_answer_breakdown': ['Given: Prove that sin^2 x + cos^2 x = 1', 'Start with the Pythagorean trigonometric identity: sin^2 x + cos^2 x = 1', 'This identity holds true for all angles x', 'Hence, sin^2 x + cos^2 x = 1 is proven']
             }
            
            question = "1. Find the radian measure of an angle subtended by an arc of length 5 units in a circle of radius 2 units."
            student_answer = 'sin^2 x + cos^2 x = 1',
            ai_explaination = ['Given: Prove that sin^2 x + cos^2 x = 1', 'Start with the Pythagorean trigonometric identity: sin^2 x + cos^2 x = 1', 'This identity holds true for all angles x', 'Hence, sin^2 x + cos^2 x = 1 is proven']
            comment = 'Good understanding of the fundamental trigonometric identity, but missing some key steps.', 
            concepts_used = ['Trigonometric identity: sin^2 x + cos^2 x = 1'],
            score = 3
            
            data['question'] = question
            data['student_answer'] = student_answer
            data['ai_explaination'] = ai_explaination
            data['comment'] = comment
            data['concepts_used'] = concepts_used
            data['obtained_marks'] = 3
            data['question_marks'] = 3
            data['total_marks'] = 30
            data['key'] = 'correct'

            question_answer.student_answer = student_answer
            question_answer.ai_answer = ai_explaination
            question_answer.ai_correct = True
            question_answer.question_marks = 3
            question_answer.ai_given_marks = 2
            question_answer.total_marks = 30
            question_answer.save()
            
            #score and 
            

            # self.Ai_validation()
        elif solve=='true':
            # Image text submit the ai model then it solve the question

            # self.Ai_validation()
            # ai_explaination = self.Ai_Explaination_step_by_step(int(class_obj.name), question)

            # question = "1. Find the radian measure of an angle subtended by an arc of length 5 units in a circle of radius 2 units."
            # ai_explaination = "Find the radian measure of an angle subtended by an arc of length 5 units in a circle with a radius of 2 units. To solve this, you can use the formula: Angle (in radians) = Arc length / Radius. In this case: The arc length is 5 units. The radius is 2 units. Using the formula: Angle = 5 / 2 = 2.5 radians. Thus, the angle subtended by the arc is 2.5 radians."
            data['question'] = question
            # data['ai_explaination'] = ai_explaination #list will come
            data['ai_explaination'] = ['Step 1: Start with the given equation: (cos θ + sin θ)^2 + (cos θ - sin θ)^2 = 2', 'Step 2: Expand the squares using the algebraic identity (a + b)^2 = a^2 + 2ab + b^2 and (a - b)^2 = a^2 - 2ab + b^2', 'Step 3: Apply the identities to the given equation: (cos θ + sin θ)^2 = cos^2 θ + 2cos θ sin θ + sin^2 θ and (cos θ - sin θ)^2 = cos^2 θ - 2cos θ sin θ + sin^2 θ', 'Step 4: Substitute the expanded forms back into the equation: (cos^2 θ + 2cos θ sin θ + sin^2 θ) + (cos^2 θ - 2cos θ sin θ + sin^2 θ) = 2', 'Step 5: Combine like terms: cos^2 θ + 2cos θ sin θ + sin^2 θ + cos^2 θ - 2cos θ sin θ + sin^2 θ', 'Step 6: Notice that the terms 2cos θ sin θ and -2cos θ sin θ cancel each other out: cos^2 θ + sin^2 θ + cos^2 θ + sin^2 θ', 'Step 7: Use the Pythagorean identity cos^2 θ + sin^2 θ = 1: 1 + 1 = 2', 'Step 8: Simplify the equation: 2 = 2', 'Step 9: Conclude that the given equation is an identity and holds true for all values of θ']
            data['obtained_marks'] = 0
            data['question_marks'] = 3
            data['total_marks'] = 30
            data['key'] = 'solve'
            # question_answer.ai_answer = ai_explaination
            # question_answer.question_marks = 3
            # question_answer.ai_given_marks = 0
            # question_answer.total_marks = 30
            # question_answer.ai_solved=True
            # question_answer.save()
            
        else:
            # Explain - with examples and concepts
  
            question = "1. Find the radian measure of an angle subtended by an arc of length 5 units in a circle of radius 2 units."
            ai_explaination = "Find the radian measure of an angle subtended by an arc of length 5 units in a circle with a radius of 2 units. To solve this, you can use the formula: Angle (in radians) = Arc length / Radius. In this case: The arc length is 5 units. The radius is 2 units. Using the formula: Angle = 5 / 2 = 2.5 radians. Thus, the angle subtended by the arc is 2.5 radians."
            data['question'] = question
            data['ai_explaination'] = ai_explaination
            data['obtained_marks'] = 0
            data['question_marks'] = 3
            data['total_marks'] = 30
            data['concepts'] = [
                    {
                        "concept": "What is the result of 2 + 3?",
                        "explanation": "Adding 2 and 3 gives a total of 5 because 2 plus 3 equals 5.",  # Explanation
                        "example-1": "7 - 2 = 5",
                        "example-2": "7 - 2 = 5"
                    },
                    {
                        "concept": "What is the result of 7 - 2?",
                        "explanation": "Subtracting 2 from 7 gives a total of 5.",
                        "example-1": "7 - 2 = 5",
                        "example-2": "7 - 2 = 5"
                    }
                ]

            data['key'] = 'explain'

            question_answer.ai_answer = ai_explaination
            question_answer.question_marks = 3
            question_answer.ai_given_marks = 0
            question_answer.total_marks = 30
            question_answer.ai_explain=True
            question_answer.save()
        
        return Response({"message": "Answer submitted successfully!", 'ai_data':data}, status=status.HTTP_201_CREATED)

        # except Exception as e:
        #     return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





    def Ai_Explaination(self, class_nums, question):
        url = "http://128.199.19.226:8080/api/generate-concepts-required/"
#        url = "http://139.59.86.115/api/generate-concepts-required/"
        print(class_nums, question)
        data = {
            "question": question,
            "class_nums": [class_nums],
            "student_level": 2
        }
        response = requests.post(url, json=data)
        print(response)
        print(response.text)
        if response.status_code == 200:
            if response.headers.get('Content-Type') == 'application/json':

                json_data = response.json()
                # data = new_replace_curly_quotes(response.json())

                question = json_data.get('question', '')
                step_by_step_solution = json_data.get('step_by_step_solution', [])
                concepts_required = json_data.get('concepts_required', [])
                # print(step_by_step_solution)
                concepts = []
                for concept in concepts_required:
                    # print(concept['concept_example'])

                    concept_dict = {
                        "concept": concept['concept_name'],
                        "explanation": concept['concept_description'],
                        "example": concept['concept_example'],
                        'chapter':concept['chapter_name']
                        # "example-2": concept['concept_example']  # Using the same example for simplicity
                    }

                    concepts.append(concept_dict)
                    # print(concept_dict['example'])
                new_stepss=[]

                if "$" in question:
                    new_string = json.loads(step_by_step_solution[0]['step'].replace('\\', '\\\\'))
                    new_string_dict=new_string['step_by_step_solution']
                    new_stepss=[]
                    for ste in new_string_dict:
                        new_stepss.append(ste['step'])
                    # print(new_stepss)
                # print(type(new_string))
                # print(new_string)

                # print(ai_explaination[0]['step']['step_by_step_solution'])
                # print(ai_explaination)
                else:
                    new_stepss=[]
                    for steps in step_by_step_solution:
                        new_stepss.append(steps['step'])
                    ai_explaination = new_stepss
                # Construct the final output
                output = {

                        "question": f"1. {question}",
                        # "ai_explaination": explanation,
                        "obtained_marks": 0,
                        "question_marks": 3,
                        "total_marks": 30,
                        "concepts": concepts,
                        "key": "explain",
                        "solution":new_stepss
                    }


                return output

        else:
            return {'error': 'Failed to retrieve data from external API'}