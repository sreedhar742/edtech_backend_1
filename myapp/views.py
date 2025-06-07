from rest_framework.response import Response
from rest_framework.views import APIView
# from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .models import classes, Subject, Topics, SubTopics 
from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from .models import classes, Subject, Topics, SubTopics, Question_Answers,GapAnalysis
from .serializers import ChapterSerializer, ClassSerializer, SubjectSerializer, TopicSerializer, SubTopicSerializer, InputSerializer,GapAnalysisSerializer
import json
import requests
import re
import base64
from .models import StudentSubmits


import base64
from datetime import datetime
import pytz
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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get all classes
            class_objects = classes.objects.all().order_by('class_code')
            # class_objects = classes.objects.filter(class_code="10")
            # Serialize the data
            serializer = ClassSerializer(class_objects, many=True)
            sorted_data = sorted(serializer.data, key=lambda x: int(x['class_code']))  # Sort by class_code as integer
            
            return Response({
                "status": "Success",
                "message": "Classes retrieved successfully",
                "data": sorted_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "status": "Error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SubjectListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get class_id from query params
            class_id = request.data.get('class_id')
            
            # Validate class_id
            if not class_id:
                return Response({
                    "status": "Error",
                    "message": "class_id is required"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get class object
            try:
                class_obj = classes.objects.get(class_code=class_id)
            except classes.DoesNotExist:
                return Response({
                    "status": "Error",
                    "message": f"Class with id {class_id} not found"
                }, status=status.HTTP_404_NOT_FOUND)

            # Get subjects for class
            subjects = Subject.objects.filter(class_name=class_obj)
            print(subjects)
            serializer = SubjectSerializer(subjects, many=True)

            return Response({
                "status": "Success",
                "message": "Subjects retrieved successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "Error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class TopicListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get subject_id and class_id from request data
            subject_code = request.data.get('subject_id')
            class_code = request.data.get('class_id')
            print(subject_code,class_code)
            
            # Validate subject_id and class_id
            if not subject_code:
                return Response({
                    "status": "Error",
                    "message": "subject_id is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not class_code:
                return Response({
                    "status": "Error",
                    "message": "class_id is required"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Verify class exists
            try:
                class_obj = classes.objects.get(class_code=class_code)
                print(class_obj)
            except classes.DoesNotExist:
                return Response({
                    "status": "Error",
                    "message": f"Class with id {class_code} not found"
                }, status=status.HTTP_404_NOT_FOUND)

            # Verify subject exists and belongs to the class
            try:
                subject = Subject.objects.get(subject_code=subject_code, class_name=class_obj)
            except Subject.DoesNotExist:
                return Response({
                    "status": "Error",
                    "message": f"Subject with id {subject_code} not found for class with id {class_code}"
                }, status=status.HTTP_404_NOT_FOUND)

            # Get topics for subject
            topics = Topics.objects.filter(subject=subject)
            serializer = TopicSerializer(topics, many=True)

            return Response({
                "status": "Success",
                "message": "Topics retrieved successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "Error", 
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     
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
def new_replace_curly_quotes(json_string):
        # Replace curly quotes with straight quotes using regex
        updated_string = re.sub(r'[“”‘’]', '"', json_string)
        
        updated_string = json_string.replace('’', "'").replace('json', '').replace("```", "'''")

        new_dict = eval(updated_string)
        data_dict = json.loads(new_dict)
        # print(data_dict,"=====------data_dict------=======")
        print(type(data_dict))
        return data_dict
#completed
class QuestionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def replace_curly_quotes(self,json_string):

        updated_string = re.sub(r'[“”‘’]', '"', json_string)
        
        updated_string = json_string.replace('’', "'").replace('json', '').replace("```", "'''")

        new_dict = eval(updated_string)
        data_dict = json.loads(new_dict)

        print(type(data_dict))
        return data_dict

    def ai_generated_questions(self, class_num, chapter_nums, type_):
        extension = ""
        if type_ == "exercise":
            extension = "generate-questions-exercises/"
        elif type_ == "solved":
            extension = "generate-questions-examples2/"
        else:
            extension = "generate-questions-external/"

        url = "http://139.59.86.115/api/" + extension
        data = {
            "class_num": class_num,
            "chapter_nums": chapter_nums
        }
        
        
        response = requests.post(url, json=data)
        # print(response.json(),'======-------data--------')
        # Check if the response status code is 200 before parsing
        if response.status_code == 200:
            # Parse the response JSON directly
            # print(response)
            response_data = response.json()
            if isinstance(response_data, dict):
                # print("response_Data",response_data)
                questions_list = [question["Question"] if question.get("Question") else question['question']for question in response_data.get("questions", [])]
                # print("from instance")
                return questions_list  
            else:
                # print(response_data, "========--------response_data---------=========")
                # print(response_data,"from raw data",type(response_data))
                updated_data = self.replace_curly_quotes(response_data)
                # print("updated_data",updated_data)
                questions_list = [question["Question"] if question.get("Question") else question['question'] for question in updated_data.get("questions", [])]
                # print("from updated_data")
                return questions_list
        else:
            # Handle errors
            print("Error: ", response.text)  # Log the error response
            return {'error': 'Failed to retrieve data from external API'}
    def post(self, request, *args, **kwargs):
        serializer = InputSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            classid = serializer.validated_data['classid']
            subjectid = serializer.validated_data['subjectid']
            topicids = serializer.validated_data['topicid']
            print(topicids)
            # topicids = topicids[0]  
            # subtopicid = serializer.validated_data['subtopicid']
            solved = serializer.validated_data.get('solved', None)
            exercise = serializer.validated_data.get('exercise', None)
            level = serializer.validated_data.get('external', None)
            class_name = classes.objects.get(class_code=classid).class_name
            # subjectname = Subject.objects.get(id=subjectid).name
            print('came')
            print(classid,"---",class_name)
            # subject=Subject.objects.get(id=subjectid)
            # print(subject)
            # if not Topics.objects.filter(subject_id=subjectid, id__in=topicids).exists():
            #     return Response({"error": "Invalid topic IDs for the given subject ID."}, status=status.HTTP_400_BAD_REQUEST)
                
            # topic_nums = [
            #     int(name.split(',', 1)[0].strip())
            #     for name in Topics.objects.filter(id__in=topicids, subject_id=subjectid)
            #                             .values_list('name', flat=True)
            # ]
            # print(topic_nums)
            topic_nums = []
            if type(topicids) == list:
                topic_nums = topicids
            else:
                for i in topicids[0]:
                    if i!=',':
                        topic_nums.append(int(i))
            print(topic_nums)
            
            # for postman
            # for i in topicids[0]:
            #     if i!=',':
            #         topic_nums.append(int(i))
            # print(topic_nums)
            # if subtopicid:
            #     subtopics = SubTopics.objects.filter(id__in=subtopicid, topic__id__in=topic_nums)
            #     subtopic_names = list(subtopics.values_list('name', flat=True))  # Get list of subtopic names


                # ai_questions = self.ai_generated_questions(int(class_name), topicids)
                

                # return Response({"message": "AI-generated questions created with subtopics.", "questions":ai_questions}, status=status.HTTP_200_OK)
            type_ = None
            
            if type_ == None:
                if solved:
                    type_="solved"
                elif exercise:
                    type_ = "exercise"
                else:
                    type_ = "externel"
                print(type_)
                print(class_name, topic_nums, type_)
                ai_questions= self.ai_generated_questions(int(class_name), topic_nums, type_)
                    
                return Response({"message": "AI-generated questions.","questions":ai_questions}, status=status.HTTP_200_OK)
                    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AnswerSubmit(APIView):
    permission_classes = [IsAuthenticated]
    
    
    # Explain 
    import requests
    import json
    import re

    def Ai_Explaination(self, class_nums, question):
        url = "http://128.199.19.226:8080/api/generate-concepts-required/"
        print(class_nums, question)

        data = {
            "question": question,
            "class_nums": [class_nums],
            "student_level": 3
        }

        try:
            response = requests.post(url, json=data)

            if response.status_code == 200 or response.status_code == 500:
                if response.headers.get('Content-Type') == 'application/json':
                    json_data = response.json()
                    
                    # Process question and step-by-step solution
                    # question = json_data.get('question', '')
                    step_by_step_solution = json_data.get('step_by_step_solution', [])
                    if response.status_code == 500:
                        concepts_raw = json_data.get('raw_content', '[]')
                    else:
                        concepts_raw = json_data.get('concepts_required', '[]')

                    # Parse concepts_required safely
                    if isinstance(concepts_raw, str):
                        try:
                            cleaned = re.sub(r'^```json\s*|\s*```$', '', concepts_raw.strip())

                            escaped_cleaned = cleaned.replace('\\', '\\\\')

                            # Now parse safely
                            concepts_required = json.loads(escaped_cleaned)
                        except json.JSONDecodeError as e:
                            print("Failed to parse concepts_required:", e)
                            concepts_required = []
                    else:
                        concepts_required = concepts_raw
                    # Extract concept details
                    concepts = []
                    for concept in concepts_required:
                        try:
                            concept_dict = {
                                "concept": concept['concept_name'],
                                "explanation": concept['concept_description'],
                                "example": concept['concept_example'],
                                "chapter": concept['chapter_name']
                            }
                            concepts.append(concept_dict)
                        except Exception as e:
                            print("Error processing concept:", e)

                    new_stepss = []
                    try:
                        if "$" in question:
                            new_string = json.loads(step_by_step_solution[0]['step'].replace('\\', '\\\\'))
                            new_string_dict = new_string['step_by_step_solution']
                            for ste in new_string_dict:
                                new_stepss.append(ste['step'])
                        else:
                            for steps in step_by_step_solution:
                                new_stepss.append(steps['step'])
                    except Exception as e:
                        print("Error processing steps:", e)
                        new_stepss = []

                    # Final output structure
                    output = {
                        "question": question,
                        "obtained_marks": 0,
                        "question_marks": 3,
                        "total_marks": 30,
                        "concepts": concepts,
                        "key": "explain",
                        "solution": new_stepss
                    }
                    print("Output:", output)    
                    return output

            else:
                print("Non-200 response:", response.status_code)
                return {"error": "API call failed", "status": response.status_code}

        except Exception as e:
            print("Exception occurred:", e)
            return {"error": str(e), "status": 500}

    # Explain - step - by - step
    def Ai_Explaination_step_by_step(self, class_nums, question):
        
        url = "http://128.199.19.226:8080/api/generate-step-by-step-solution/"
        data = {
            "question": question,
            "class_nums": [class_nums]
        }
        
        response = requests.post(url, json=data)
        print("response status code :",response.status_code)
        print("response is :",response)
        print("response_text is :",response.text)
        
        if response.status_code == 200:
            if response.headers.get('Content-Type') == 'application/json':
                json_data = response.json()
                # print(json_data)
                # data = n ew_replace_curly_quotes(response.json())
                # print(json_data['step_by_step_solution'],"=====---json_data['step_by_step_solution']---====")
                return json_data['step_by_step_solution']
        else:
            return Response({'error': 'Failed to retrieve data from external API'}, status=response.status_code)

    def parse_data(self, data):
        # print(data)
        # json_start = data['raw_result'].find('{')
        # json_end = data['raw_result'].rfind('}') + 1
        # raw_json = data['raw_result'][json_start:json_end]

        # # Convert JSON string to a Python dictionary
        # parsed_json = json.loads(raw_json)
        return data

    def Ai_jpg_to_text_converter(self,image_binary):
        # import base64
        url = self.new_method()
        
        # image = base64.b64encode(image_path.read()).decode('utf-8')
    
        # return 
        # print(image,"========-------image-----=========")
        
        data = {"image":image_binary}
        
        response = requests.post(url,json=data)
        # print("response is :",response)
        # print("response_text is :",response.text)
        if response.status_code == 200:
            dict_data = response.json()
            # print(dict_data)
            print("dic_data is :",dict_data)
            result = dict_data['result']
            return result
        else:
            # return Response({'error': 'Failed to retrieve data from external API'}, status=response.status_code)
            return "Student answer is not uploaded"

    def new_method(self):
        url = "http://139.59.86.115/api/img-to-txt/"
        return url
    
    def autoscore(self, student_answer_base64, question_text,q_image_binary):
        import tempfile
        import os
        import base64
        auto_score_url = "http://128.199.19.226:8080/api/auto-score/"
        question_fig_base64 = q_image_binary
        # print(question_fig_base64)
        # print(student_answer_base64)
        # Create a temporary file to store the base64 decoded image
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            # Decode base64 string to binary
            try:
                # Remove data:image/png;base64, prefix if present
                if ';base64,' in student_answer_base64:
                    student_answer_base64 = student_answer_base64.split(';base64,')[1]
                if 'data:image/png;base64,' in  question_fig_base64:
                    question_fig_base64 = question_fig_base64.split('data:image/png;base64,')[1]
                image_data = base64.b64decode(student_answer_base64)
                temp_file.write(image_data)
                temp_file.flush()
                   
                data = {
                        "question_text": question_text,
                        "question_fig_base64": question_fig_base64
                    }
                # print(data)
                # Open the temporary file and send it as multipart form data
                with open(temp_file.name, 'rb') as image_file:
                    files = {
                        "answer_image": ('image.png', image_file, 'image/png')
                    }
                    
                    response = requests.post(auto_score_url, data=data, files=files)
                    # print(response)
                    # 
                    # print(response.text)
                    
                    if response.status_code == 200:
                        dict_data = self.parse_data(response.json())
                        # print(dict_data)
                        return dict_data
                    else:
                        return {"error": f"API request failed with status code {response.status_code}"}
                    
            except Exception as e:
                return {"error": f"Failed to process image: {str(e)}"}
            finally:
                # Clean up the temporary file
                try:
                    os.unlink(temp_file.name)
                except Exception as e:
                    print(f"Failed to delete temporary file: {str(e)}")
    
    def post(self, request, *args, **kwargs):
        
        session_key = request.headers.get('SessionKey')

        class_id = request.POST.get('class_id')
        subject_id = request.POST.get('subject_id')
        question = request.POST.get('question')

        subtopic = request.POST.get('subtopic')
        submit = request.POST.get('submit')
        solve = request.POST.get('solve')
        correct = request.POST.get('correct')
        explain = request.POST.get('explain')
        chapter=request.POST.get('topic_ids')
        student_time=request.POST.get('study_time_seconds')
        print(student_time)
        if not student_time:
            student_time = 0
        timezone_name = "Asia/Kolkata"
        timezone = pytz.timezone(timezone_name)
        current_time = datetime.now(timezone)
        subject_name = Subject.objects.get(class_name__class_code=class_id,subject_code=subject_id).subject_name
        
        gap_analysis_object=GapAnalysis.objects.create(student=request.user, class_name=class_id, subject=subject_name, chapter_number=chapter, question_text=question, session_key=session_key,date=current_time,student_answering_time=int(student_time))
        if 'ques_img' in request.POST:
            gap_analysis_object.question_image_base64 = request.POST.get('ques_img')
        else:
            gap_analysis_object.question_image_base64 = "No image for question"
        blank_file="iVBORw0KGgoAAAANSUhEUgAAB4AAAAQ4CAYAAADo08FDAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAACiySURBVHhe7dkBDQAADMOg+ze9+2jABjcAAAAAAAAAEgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAACQsD3xz9NpPFRbdgAAAABJRU5ErkJggg=="

        if 'ques_img' in request.POST:
            q_image_binary= request.POST.get('ques_img')
      
        else:
            q_image_binary = blank_file

        if 'ans_img' in request.FILES:
            image = request.FILES.get('ans_img')
            image_binary = base64.b64encode(image.read()).decode('utf-8')
        else:
            image_binary = "image not submitted"
        gap_analysis_object.student_answer_base64 = image_binary
        print("request is successfull")
        

        class_obj = classes.objects.get(class_code=str(class_id))
        print(class_obj)

        topic_ids_str = request.POST.get('topic_ids')  # This may come as a comma-separated string
 
        if topic_ids_str:
            topic_ids = [int(tid) for tid in topic_ids_str.split(',')] 
            # Ensure all required fields are present
        
        timezone_name = "Asia/Kolkata"
        timezone = pytz.timezone(timezone_name)
        current_time = datetime.now(timezone)
        gap_analysis_object.date = current_time
        question_answer = Question_Answers.objects.create(
            user=request.user,
            question_text=question,
            answer_image=image_binary,
            date=current_time
        )
        
        # print(image_binary)
        
        if topic_ids:
            topics = Topics.objects.filter(id__in=topic_ids)  # Get all topics by IDs
            question_answer.topic.set(topics)  # Set only the topics received in topic_ids


        

        question_answer.save()
        
        
        data={}
        # print(request.POST)

        if submit=='true':
            print("submitted")
            img_to_txt = self.Ai_jpg_to_text_converter(image_binary)
            # print(img_to_txt)
            # question = "1. Find the radian measure of an angle subtended by an arc of length 5 units in a circle of radius 2 units."
            
            # student_answer = img_to_txt['result']
            gap_analysis_object.student_score=0
            gap_analysis_object.answering_type="submit"
            gap_analysis_object.student_answer = img_to_txt
            gap_analysis_object.save()
            data['question'] = question
            data['student_answer'] = img_to_txt
            data['question_marks'] = 10
            data['obtained_marks'] = 0
            data['total_marks'] = 10
            data['key'] = 'submit'
            question_answer.ai_submit = True
            question_answer.solved = True
            question_answer.student_answer = img_to_txt
            # question_answer.question_marks = 3
            # question_answer.ai_given_marks = 2
            # question_answer.total_marks = 30
            question_answer.save()
            
            # send image 
        elif correct=='true':
            ai_corr = self.autoscore(image_binary, question,q_image_binary)
            
            data['question'] = question
            data['student_answer'] = ai_corr['student_answer_replication']
            gap_analysis_object.answering_type="correct"
            gap_analysis_object.student_answer = ai_corr['student_answer_replication']
            gap_analysis_object.student_score=ai_corr['score']
            gap_analysis_object.comment=ai_corr['comment']
            gap_analysis_object.concept_answer=ai_corr['concepts_used']
            gap_analysis_object.ai_answer = ai_corr['correct_answer_breakdown']
            gap_analysis_object.save()
            data['ai_explaination'] = ai_corr['correct_answer_breakdown']
            data['comment'] = ai_corr['comment']
            data['concepts_used'] = ai_corr['concepts_used']
            data['obtained_marks'] = ai_corr['score']
            data['question_marks'] = 10
            data['total_marks'] = 10
            data['key'] = 'correct'
            if ai_corr['question_image_base64']==blank_file:
                data['question_image_base64']=""
            else:
                data['question_image_base64']=ai_corr['question_image_base64']

            question_answer.student_answer = ai_corr['student_answer_replication']
            
            question_answer.ai_answer = ai_corr['correct_answer_breakdown']
            question_answer.ai_correct = True
            question_answer.question_marks = 10
            question_answer.ai_concepts=ai_corr['concepts_used']
            question_answer.ai_given_marks = ai_corr['score']
            question_answer.total_marks = 10
            question_answer.save()
            
            #score and 
            

            # self.Ai_validation()
        elif solve=='true':
           
            ai_explaination = self.Ai_Explaination_step_by_step([int(class_obj.class_name)], question)

            new_stepss=[]
            if "$" in question:
                new_string = json.loads(ai_explaination[0]['step'].replace('\\', '\\\\'))
                new_string_dict=new_string['step_by_step_solution']
                new_stepss=[]
                for ste in new_string_dict:
                    new_stepss.append(ste['step'])  
            else:
                new_stepss=[]
                for steps in ai_explaination:
                    new_stepss.append(steps['step'])
            ai_explaination = new_stepss
            data['question'] = question
            data['ai_explaination'] = new_stepss
            data['obtained_marks'] = 0

            data['question_marks'] = 10
            data['total_marks'] = 10
            data['key'] = 'solve'
            gap_analysis_object.answering_type="step_by_step"
            gap_analysis_object.student_answer = "not solved"
            gap_analysis_object.student_score=0
            gap_analysis_object.save()
            question_answer.ai_answer = ai_explaination
            question_answer.question_marks = 10
            question_answer.ai_given_marks = 0
            question_answer.total_marks = 10
            question_answer.ai_solved=True
            question_answer.save()
            
        else:
           
            class_name=classes.objects.get(class_code=class_id).class_name
            data = self.Ai_Explaination(int(class_name), question)
  
            question_answer.ai_answer = data
            question_answer.question_marks = 10
            question_answer.ai_given_marks = 0
            question_answer.total_marks = 10
            question_answer.ai_explain=True
            question_answer.save()
            gap_analysis_object.answering_type="explain"
            gap_analysis_object.student_answer = "not solved"
            gap_analysis_object.student_score=0
            gap_analysis_object.save()
        # gap_analysis_data = {
        #     'student': request.user.fullname,
        #     'class_name': gap_analysis_object.class_id,
        #     'subject': gap_analysis_object.subject_name,
        #     'question_text': gap_analysis_object.question,
        #     'student_answer_base64': image_binary,
        #     'topic_ids': chapter,
        #     'date': current_time.isoformat(),  # Store as ISO string
        #     'question_image_base64': gap_analysis_object.question_image_base64,
        #     'student_answer': gap_analysis_object.student_answer,
        #     'student_score': gap_analysis_object.student_score,
        #     'answering_type': gap_analysis_object.answering_type,
        # }
        if 'gap_analysis_data' not in request.session:
            request.session['gap_analysis_data'] = []

        # Append the current gap_analysis_object to the session list
        request.session['gap_analysis_data'].append(GapAnalysisSerializer(gap_analysis_object).data)
        # Mark the session as modified to ensure changes are saved
        request.session.modified = True
        
        return Response({"message": "Answer submitted successfully!", 'ai_data':data}, status=status.HTTP_201_CREATED)

import re
class StudentSubmitAPIView(APIView):
    permission_classes = [IsAuthenticated]
      # Disable authentication

    def post(self, request, *args, **kwargs):
        student = request.user
        question = request.data.get('question')
        image = request.FILES.get('image')

        if not image or not question:
            return Response({"error": "Image and question are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Convert image to binary64
        image_binary = base64.b64encode(image.read()).decode('utf-8')
        # if image_binary:
        #     print("yes")
        #     Save the image and question to the database
        timezone_name = "Asia/Kolkata"
        timezone = pytz.timezone(timezone_name)
        current_time = datetime.now(timezone)
        student_submit = StudentSubmits.objects.create(
            student=student,
            image=image_binary,
            question=question,
            date_time=current_time
        )

        # Make an API call with the binary64 image and question
        # url = "http://139.59.86.115:8000/api/img-to-txt/"
        # data = {"image": image_binary}
        # response = requests.post(url, json=data)
        # print(response)
        # if response.status_code == 200:
        #     response_data = response.json()
        #     student_answer = response_data.get('student_answer')

        #     # Update the student_answer field
        #     student_submit.student_answer = student_answer
        #     student_submit.save()

        #     # Make another API call with the student_answer and question
        #     url = "http://139.59.86.115:8000/api/auto-score/"
        #     data = {"student_answer": student_answer, "question": question}
        #     response = requests.post(url, json=data)

        #     if response.status_code == 200:
        #         response_data = response.json()
        #         student_submit.correction_text = response_data.get('correction_text')
        #         student_submit.mistakes = response_data.get('mistakes')
        #         student_submit.question_marks = response_data.get('question_marks')
        #         student_submit.student_marks = response_data.get('student_marks')
        #         student_submit.save()

        #         return Response({"message": "Submission processed successfully."}, status=status.HTTP_200_OK)
        #     else:
        #         return Response({"error": "Failed to score the answer."}, status=response.status_code)
        # else:
        #     return Response({"error": "Failed to convert image."}, status=response.status_code)
        data = {
            "student_answer": "trigonometry is an chapter it is used to calculate the heights.",
            "question_text": question,
            "ideal_solution": "",
            "pattern_info": ""
        }
        url = "http://139.59.86.115:8000/api/auto-score/"
        
        response = requests.post(url, json=data)
        print(response.text)
        print(response.status_code)
        if response.status_code == 500:
            response_data = response.json()
            
            json_start = response_data['raw_result'].find('{')
            json_end = response_data['raw_result'].rfind('}') + 1
            raw_json = response_data['raw_result'][json_start:json_end]
            
            parsed_json = json.loads(raw_json)
            print(parsed_json)
            
            student_submit.correction_text = response_data.get('correction_text')
            student_submit.mistakes = response_data.get('mistakes')
            student_submit.question_marks = response_data.get('question_marks')
            student_submit.student_marks = response_data.get('student_marks')
            student_submit.score = parsed_json.get('score')
            student_submit.comment = parsed_json.get('comment')
            student_submit.concepts_used = parsed_json.get('concepts_used')
            student_submit.student_answer_replication = parsed_json.get('student_answer_replication')
            student_submit.correct_answer_breakdown = parsed_json.get('correct_answer_breakdown')
            student_submit.save()

            return Response({"message": "Submission processed successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to score the answer."}, status=response.status_code)

from rest_framework.parsers import MultiPartParser, FormParser
from .models import QuestionWithImage
from .serializers import QuestionWithImageSerializer
import csv
from io import StringIO
import chardet

class QuestionWithImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES['file']
        if not file.name.endswith('.csv'):
            return Response({"error": "Only CSV files are allowed."}, status=status.HTTP_400_BAD_REQUEST)
        print("file is received")
        
        # Detect file encoding
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        
        file_data = raw_data.decode(encoding)
        csv_data = csv.reader(StringIO(file_data))
        next(csv_data)  # Skip header row
        print("file readed")
        for row in csv_data:
            print(len(row))
            print(row)
            # if len(row) != 6:
            #     return Response({"error": "CSV file format is incorrect. Expected 6 columns."}, status=status.HTTP_400_BAD_REQUEST)
            
            class_code, subject_code, topic_code, sup_topic_code, question, question_image,typed = row[:7]
            if class_code!="":
                QuestionWithImage.objects.create(
                    class_code=class_code,
                    subject_code=subject_code,
                    topic_code=topic_code,
                    question=question,
                    question_image=question_image,
                    typed=typed,
                    sub_topic_code=sup_topic_code
                )
            
        print("successfully uploaded")
        return Response({"message": "Questions with images uploaded successfully."}, status=status.HTTP_201_CREATED)


import base64
from openai import OpenAI

client = OpenAI(
    api_key="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",
)

def extract_question_from_base64(image_binary):
    # Read and encode the image as base64
    
    encoded_image = image_binary

    # Create GPT-4o chat completion with vision
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an OCR assistant. Extract question text only."},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "Please extract all readable text from this image and format it as a JSON object."
                    }
                ]
            }
        ]
    )
    response_text=response.choices[0].message.content
    if response_text.startswith("```json"):
        response_text = re.sub(r"^```json\s*|\s*```$", "", response_text, flags=re.DOTALL).strip()
    try:
        parsed_json = json.loads(response_text)
    except json.JSONDecodeError as e:
        print("❌ Failed to parse JSON:", e)
        print("🔍 Raw response was:\n", response_text)
        return {"error": "Invalid JSON returned from GPT", "raw": response_text}

    return parsed_json



class ChatbotAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        message = request.data.get('message')
        # print(message)
        question_text = request.data.get('question_text')
        # print(request.data)
        # quote="try to act like an chatbot and give the answer in addition don't user python keyword or pythonic solution"
        if message=="solve":
            BASE_URL = "http://128.199.19.226:8080/api/generate-step-by-step-solution/"
        # BASE_URL = "http://139.59.86.115/api/generate-concepts-required/"
            class_nums = [10]
            data = {
                "question": question_text,
                "class_nums": [class_nums]
            }
            if "$" in question_text:
                class_nums=12
            else:
                class_nums=10
            
            response = requests.post(BASE_URL, json=data)  
            # print(response)
            if response.status_code == 200:
                response = response.json()
     
                response_data=response['step_by_step_solution']
                new_stepss=[]
                if class_nums==12:
                    new_string = json.loads(response_data[0]['step'].replace('\\', '\\\\'))
                    new_string_dict=new_string['step_by_step_solution']
                    new_stepss=[]
                    for ste in new_string_dict:
                        new_stepss.append(ste['step'])  
                # print(type(new_string))
                # print(new_string)
                
                # print(ai_explaination[0]['step']['step_by_step_solution'])
                # print(ai_explaination)
                else:
                    new_stepss=[]
                    for steps in response_data:
                        new_stepss.append(steps['step'])
                final_solution = {'step_by_step_solution': new_stepss}

                return Response(final_solution, status=status.HTTP_200_OK)
        if message=="explain":  
            BASE_URL = "http://128.199.19.226:8080/api/generate-concepts-required/"
        # BASE_URL = "http://139.59.86.115/api/generate-concepts-required/"
            class_nums = [10]
            data = {
                "question": question_text,
                "class_nums": [class_nums],
                "student_level": 2
            }
            response = requests.post(BASE_URL, json=data)  
            # print(response)
            if response.status_code == 200:
                response_data = response.json()
                
                concepts = response_data['concepts_required']
                step_by_step_concepts=[]
                for idx,concepts in enumerate(concepts):
                    number=idx+1
                    conceptname="concept_name_"+str(idx+1)+"\n"+concepts['concept_name']
                    step_by_step_concepts.append(conceptname)
                    conceptdescription="concept_description: \n"+concepts['concept_description']
                    step_by_step_concepts.append(conceptdescription)
                    conceptexample="concept_example: \n"+concepts['concept_example']
                    step_by_step_concepts.append(conceptexample)
                final_solution={'step_by_step_solution': step_by_step_concepts}
                return Response(final_solution, status=status.HTTP_200_OK) 
        if request.FILES.get('ans_img') and message=="correct":
            blank_file="iVBORw0KGgoAAAANSUhEUgAAB4AAAAQ4CAYAAADo08FDAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAACiySURBVHhe7dkBDQAADMOg+ze9+2jABjcAAAAAAAAAEgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAAAQIYABAAAAAAAAIgQwAAAAAAAAQIQABgAAAAAAAIgQwAAAAAAAAAARAhgAAAAAAAAgQgADAAAAAAAARAhgAAAAAAAAgAgBDAAAAAAAABAhgAEAAAAAAAAiBDAAAAAAAABAhAAGAAAAAAAAiBDAAAAAAAAAABECGAAAAAAAACBCAAMAAAAAAABECGAAAAAAAACACAEMAAAAAAAAECGAAQAAAAAAACIEMAAAAAAAAECEAAYAAAAAAACIEMAAAAAAAAAAEQIYAAAAAAAAIEIAAwAAAAAAAEQIYAAAAAAAAIAIAQwAAAAAAACQsD3xz9NpPFRbdgAAAABJRU5ErkJggg=="

            if 'ques_img' in request.POST:
                q_image_binary= request.POST.get('ques_img')
            else:
                q_image_binary = blank_file

            if 'ans_img' in request.FILES:
                image = request.FILES.get('ans_img')
                image_binary = base64.b64encode(image.read()).decode('utf-8')
            else:
                image_binary = "image not submitted"
            correct_obj=AnswerSubmit()
            comment=correct_obj.autoscore(image_binary,question_text,q_image_binary)
            
            correct_solution=[comment['comment']]
            final_solution={'step_by_step_solution': correct_solution}                
            return Response(final_solution, status=status.HTTP_200_OK)
        
        if request.FILES.get('ans_img'):
            if 'ans_img' in request.FILES:
                image = request.FILES.get('ans_img')
                image_binary = base64.b64encode(image.read()).decode('utf-8')
            output=extract_question_from_base64(image_binary)
            print(output)
            print(type(output))
            question=""
            for key,value in output.items():
                question+=output[key]
                
            BASE_URL = "http://128.199.19.226:8080/api/generate-step-by-step-solution/"
            class_nums = [10]
            data = {
                "question": question,
                "class_nums": [class_nums]
            }
            response = requests.post(BASE_URL, json=data)  
            # print(response)
            if response.status_code == 200:
                response_data = response.json()
                print(response_data)
                solution=[]
                for steps in response_data['step_by_step_solution']:
                    solution.append(steps['step'])
                final_solution = {'step_by_step_solution': solution}

                return Response(final_solution, status=status.HTTP_200_OK)
            
            
        if message:
            BASE_URL = "http://128.199.19.226:8080/api/generate-step-by-step-solution/"
        # BASE_URL = "http://139.59.86.115/api/generate-concepts-required/"
            class_nums = [10]
            data = {
                "question": message,
                "class_nums": [class_nums]
            }
            response = requests.post(BASE_URL, json=data)  
            # print(response)
            if response.status_code == 200:
                response_data = response.json()
                print(response_data)
                solution=[]
                for steps in response_data['step_by_step_solution']:
                    solution.append(steps['step'])
                final_solution = {'step_by_step_solution': solution}

                return Response(final_solution, status=status.HTTP_200_OK)
        else:   
            return Response({"error": "Failed to retrieve data from external API."}, status=response.status_code)

from random import sample

class QuestionImageview(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        class_code = request.data.get('classid')
        subject_code = request.data.get('subjectid')
        topic_code = request.data.get('topicid')
        solved = request.data.get('solved')
        # print(solved)
        exercise = request.data.get('exercise')
        external = request.data.get('external')
        
        subtopic=request.data.get('subtopic')
        if not isinstance(topic_code, list):
            topic_code = [topic_code]
        
        if not class_code or not subject_code or not topic_code:
            return Response({"error": "class_code, subject_code, and topic_code are required."}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # If external is selected, return unique subtopics
        if external:
            # Get unique subtopics for the given filters
            subtopics = QuestionWithImage.objects.filter(
                class_code=class_code,
                subject_code=subject_code,
                topic_code__in=topic_code
            ).values_list('sub_topic_code', flat=True).distinct()

            # Remove any None/empty values and convert to list
            subtopics = [st for st in subtopics if st]

            return Response({"subtopics": subtopics})

        # For solved and exercise cases, keep existing logic
        typed = 'solved' if solved == 'true' else 'exercise' if exercise == 'true' else 'external'
        
        # Create an empty list to store all questions
        all_questions = []
        # Get questions for each topic
        # print(all_questions)
        if subtopic:
            for topic in topic_code:
                questions = QuestionWithImage.objects.filter(
                    class_code=class_code,
                    subject_code=subject_code,
                    topic_code=topic,
                    sub_topic_code=subtopic,
                ).order_by('?')[:]
                all_questions.extend(questions)
            print(all_questions)
            all_questions = sorted(all_questions, key=lambda q: q.question)
            serializer = QuestionWithImageSerializer(all_questions, many=True)
            return Response({"questions": serializer.data})
        
        all_questions = []

        # Get questions for each topic
        for topic in topic_code:
            questions = QuestionWithImage.objects.filter(
                class_code=class_code,
                subject_code=subject_code,
                topic_code=topic
            ).order_by('?')[:5]  # Get 5 random questions per topic
            all_questions.extend(questions)
        
        # If we have more than 5 questions in total, randomly select 5
        if len(all_questions) > 5:
            all_questions = sample(all_questions, 5)
        print(all_questions)
        serializer = QuestionWithImageSerializer(all_questions, many=True)
        return Response({"questions": serializer.data})

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

import re
apikey=""
class SimilarQuestionsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def generate_similar_question(self, question):
        """Generate a similar question for conceptual understanding."""
        llm = ChatOpenAI(model_name="gpt-4o",api_key=apikey)
        
        system_prompt = """You are an educational assistant. Given a question, 
        generate 1 similar question that tests the same concept in a different way.
        The question should test understanding, not just memorization.
        Provide only the question without any additional text or formatting."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Original question: {question}")
        ]
        # print(response)
        try:
            print("hello")
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            print("🔥 Error from LLM:", str(e))
            return Response({"error": str(e)}, status=500)
        response = llm.invoke(messages)
        return response.content
    
    def get_theoretical_explanation(self, question):
        """Get theoretical knowledge and explanation for the given question."""
        llm = ChatOpenAI(model_name="gpt-4o",api_key=apikey)
        
        system_prompt = """You are an expert educational tutor. For the given question, provide a detailed and structured explanation in the following format:

        1. CORE CONCEPTS:
           - List and explain each fundamental concept involved
           - Define any important terms
           - Show how these concepts are interconnected
        
        2. DETAILED EXPLANATION:
           - Break down the concept into smaller, digestible parts
           - Use analogies or real-world examples where helpful
           - Explain the logical progression of ideas
           - Include visual descriptions or diagrams where relevant
        
        3. PROBLEM-SOLVING APPROACH:
           - Step-by-step method to solve such problems
           - Common pitfalls to avoid
           - Key points to remember
        
        4. FORMULAS AND PRINCIPLES:
           - List all relevant formulas
           - Explain what each variable means
           - When and why to use each formula
        
        5. PRACTICAL APPLICATIONS:
           - Real-world applications of these concepts
           - How this knowledge is used in practice
        
        Ensure clarity, technical accuracy, and logical flow of ideas."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Please explain this question: {question}")
        ]
        
        response = llm.invoke(messages)
        cleantext=self.clean_text(response.content)
        return cleantext
    

    def clean_text(self,input_text):
        """Cleans and formats the given input text by removing LaTeX syntax, extra spaces, and structuring it neatly."""
        # Remove LaTeX syntax for mathematical expressions
        cleaned_text = re.sub(r'\\[(){}\[\]]', '', input_text)  # Remove escaped brackets
        cleaned_text = re.sub(r'\\frac{([^}]*)}{([^}]*)}', r'(\1 / \2)', cleaned_text)  # Convert fractions
        cleaned_text = re.sub(r'\\sqrt{([^}]*)}', r'sqrt(\1)', cleaned_text)  # Convert square roots
        cleaned_text = re.sub(r'\\pm', '+/-', cleaned_text)  # Convert plus-minus symbol
        cleaned_text = re.sub(r'\\times', '*', cleaned_text)  # Convert multiplication symbol
        cleaned_text = re.sub(r'\\[a-zA-Z]+', '', cleaned_text)  # Remove other LaTeX commands
        
        # Remove bold markers and extra newlines
        cleaned_text = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned_text)
        cleaned_text = re.sub(r'\n{2,}', '\n', cleaned_text)  # Reduce multiple newlines to a single newline
        
        # Trim whitespace
        cleaned_text = cleaned_text.strip()
        
        return cleaned_text

    def post(self, request, *args, **kwargs):
        question = request.data.get('question')
        
        if not question:
            return Response(
                {"error": "Please provide a question"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            similar_question = self.generate_similar_question(question)
            theory_concepts = self.get_theoretical_explanation(question)
        except Exception as e:
            return Response(
                {"error": f"Failed to generate response: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        response_data = {
            "original_question": question,
            "similar_question": similar_question,
            "theory_concepts": theory_concepts
        }
        print(response_data)
        return Response(response_data, status=status.HTTP_200_OK)

class HistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        history_entries = GapAnalysis.objects.filter(student=user).values(
            'subject',
            'chapter_number',
            'question_text',
            'student_answer',
            'student_score',
            'answering_type',
            'date'
        ).order_by('-date')[:3]  # 💥 Get only the last 3

        return Response({
            "status": "success",
            "data": list(history_entries)
        }, status=status.HTTP_200_OK)

class GapAnalysisAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        chapter_number = request.data.get('chapter_number')
        class_name=request.data.get('class_name')
        print(chapter_number)
        print(type(chapter_number))

        if not chapter_number:
            return Response({
                "status": "error",
                "message": "chapter_number is required in query parameters."
            }, status=status.HTTP_400_BAD_REQUEST)

        chapter_numbers = []
        if isinstance(chapter_number, str):
            chapter_numbers = chapter_number.split(',')
        elif isinstance(chapter_number, list):
            chapter_numbers = [str(ch) for ch in chapter_number]

        gap_entries = []
        for chapter in chapter_numbers:
            entries = GapAnalysis.objects.filter(
                student=user,
                chapter_number=chapter,
                class_name=class_name
            ).values(
                'class_name',
                'subject',
                'chapter_number',
                'question_text',
                # 'question_image_base64',
                # 'student_answer_base64',
                'student_answer',
                'student_score',
                'concept_answer',
                'student_answering_time',
                'comment',
                'ai_answer',
                'answering_type',
                'date'
            )
            gap_entries.extend(entries)

        return Response({
            "status": "success",
            "data": list(gap_entries)
        }, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
import pytz

class UserGapAnalysisDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get_user_gap_analysis_data(self, request):
        """
        Retrieves and filters the user's gap analysis data from the session.
        """
        user_id = request.user.id  # Get the current user's ID
        gap_analysis_data = request.session.get('gap_analysis_data', [])
        
        # Filter the data to get only the entries for the current user
        user_gap_analysis_data = [data for data in gap_analysis_data if data['student'] == user_id]
        
        return user_gap_analysis_data

    def get(self, request, *args, **kwargs):
        """
        API endpoint to get the gap analysis data for the authenticated user.
        """
        # Retrieve the user's gap analysis data from the session
        user_gap_analysis_data = self.get_user_gap_analysis_data(request)
        
        if not user_gap_analysis_data:
            # If no data is found, return a 404 response
            return Response({"message": "No gap analysis data found for this user."}, status=status.HTTP_404_NOT_FOUND)

        # If data is found, return the data in the response
        return Response({"gap_analysis_data": user_gap_analysis_data}, status=status.HTTP_200_OK)

class Questionupdateview(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # question_id = request.data.get('question_id')
        question_subtopic=request.data.get('subtopic')
        question_text = request.data.get('question_text')
        question_image = request.FILES.get('question_image')
        print("request is successfull")
        print(question_subtopic)
        print(question_text)
        # print(question_image)
        if not question_text:
            return Response({"error": "Question ID and text are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            question = QuestionWithImage.objects.get(question=question_text)
            question.question = question_text
            if question_image:
                question.question_image = question_image
                print("image is updated")
            if question_subtopic:
                question.sub_topic_code = question_subtopic
                print("subtopic is updated")
            question.save()
            return Response({"message": "Question updated successfully."}, status=status.HTTP_200_OK)
        except QuestionWithImage.DoesNotExist:
            return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)



class UserAverageScoreAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        # Get all unique chapter numbers for the user
        chapter_numbers = GapAnalysis.objects.filter(student=user).values_list('chapter_number', flat=True).distinct()

        if not chapter_numbers:
            return Response({"error": "No gap analysis data found for the user."}, status=status.HTTP_404_NOT_FOUND)
        
        average_scores = {}
        for chapter_number in chapter_numbers:
            # Filter GapAnalysis objects for the current user and chapter
            gap_analysis_objects = GapAnalysis.objects.filter(
                student=user,
                chapter_number=chapter_number
            )
            # print(gap_analysis_objects)
            if gap_analysis_objects.exists():
                # Calculate the average score for the chapter
                # print(total_score)
                total_score = sum(getattr(obj, 'student_score', 0) or 0 for obj in gap_analysis_objects)
                # print(total_score)     
                average_score = total_score / gap_analysis_objects.count()
                average_scores[chapter_number] = average_score
            else:
                average_scores[chapter_number] = 0  # Or handle the case where there's no data for the chapter
        print(average_scores)
        return Response(average_scores, status=status.HTTP_200_OK)
    
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from rest_framework.permissions import IsAuthenticated  # Remove import
from .models import GapAnalysis
from .serializers import GapAnalysisSerializer
from Users.models import Student  # Import the Student model
from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
class AllStudentGapAnalysisAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Remove permission class
    @csrf_exempt
    def get(self, request, *args, **kwargs):
        """
        API endpoint to retrieve all gap analysis records for all students,
        formatted as {student_id: [gap_analysis_data], ...}.
        """
        try:
            # Get all students
            students = Student.objects.all()
            
            # Prepare the data structure to hold the results
            gap_analysis_data = {}

            # Iterate over each student
            for student in students:
                # Retrieve all GapAnalysis objects for the current student
                gap_analysis_records = GapAnalysis.objects.filter(student=student)

                # Serialize the data for the current student
                serializer = GapAnalysisSerializer(gap_analysis_records, many=True)

                # Add the serialized data to the results dictionary, using student ID as key
                gap_analysis_data[student.username] = serializer.data

            # Return the formatted data in the response
            return Response({
                "status": "success",
                "data": gap_analysis_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
class LeaderboardApiView(APIView):
    
    def get(self, request, *args, **kwargs):
        """
        API endpoint to retrieve the leaderboard data for all students.
        Returns a list of students with their average scores, sorted by score in descending order.
        """
        try:
            # Get all students
            students = Student.objects.filter(is_student=True).order_by('username')
            
            # Prepare the leaderboard data
            leaderboard_data = []

            for student in students:
                # Calculate the average score for each student
                gap_analysis_records = GapAnalysis.objects.filter(student=student)
                if gap_analysis_records.exists():
                    total_score = sum(getattr(record, 'student_score', 0) or 0 for record in gap_analysis_records)
                    average_score = total_score / gap_analysis_records.count()
                else:
                    average_score = 0
                
                leaderboard_data.append({
                    'student_id': student.id,
                    'username': student.username,
                    'average_score': average_score
                })

            # Sort the leaderboard data by average score in descending order
            leaderboard_data.sort(key=lambda x: x['average_score'], reverse=True)

            return Response({
                "status": "success",
                "data": leaderboard_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            



from .models import Homework
from .serializers import HomeworkSerializer

class AddHomeworkAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print(request.data)
        teacher = request.user
        if not getattr(teacher, 'is_teacher', False):
            return Response({"error": "Only teachers can add homework."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = HomeworkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(teacher=teacher)
            return Response({"message": "Homework added successfully.", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from myapp.models import Notification
from myapp.serializers import NotificationSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


from myapp.models import Notification
from myapp.serializers import NotificationSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class StudentNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Only allow students to access this endpoint
        if getattr(request.user, 'is_teacher', False):
            return Response(
                {"detail": "Not authorized. This endpoint is for students only."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        student = request.user

        # Get the last notification where sender and student belong to the same class
        notification = Notification.objects.filter(
            sender__class_name=student.class_name
        ).order_by('-timestamp').first()

        if notification:
            # Check if the student has already submitted this homework
            from .models import HomeworkSubmission
            has_submitted = HomeworkSubmission.objects.filter(
                homework=notification.homework,
                student=student
            ).exists()
            if has_submitted:
                return Response(
                    {"message": "No notifications found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = NotificationSerializer(notification)
            return Response(serializer.data)
        else:
            return Response(
                {"message": "No notifications found."},
                status=status.HTTP_404_NOT_FOUND
            )
            
from .models import HomeworkSubmission
from .serializers import HomeworkSubmissionSerializer

class HomeworkSubmissionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data

        print(request.data)
        homework_code = data.get('homework_code')
        submitted_file = data.get('submitted_file')
        score = data.get('score')  # Optional
        feedback = data.get('feedback')  # Optional

        try:
            homework = Homework.objects.get(homework_code=homework_code)
        except Homework.DoesNotExist:
            return Response({"error": "Invalid homework code."}, status=status.HTTP_400_BAD_REQUEST)

        submission = HomeworkSubmission.objects.create(
            homework=homework,
            student=request.user,
            submitted_file=submitted_file,
            score=score,
            feedback=feedback
        )

        return Response({
            "message": "Homework submitted successfully.",
            "submission_id": submission.id
        }, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        submissions = HomeworkSubmission.objects.filter(student=request.user)
        serializer = HomeworkSubmissionSerializer(submissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)