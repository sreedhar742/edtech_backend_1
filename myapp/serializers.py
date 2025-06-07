from .models import classes, Subject, Topics, SubTopics, StudentSubmits, Question_Answers, QuestionWithImage
from .models import GapAnalysis 
from rest_framework import serializers

class SubTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTopics
        fields = ['id', 'name']

class ChapterSerializer(serializers.ModelSerializer):
    topics = SubTopicSerializer(many=True, required=False)

    class Meta:
        model = Topics
        fields = ['id', 'name', 'subject', 'topics']
    
    def create(self, validated_data):
        topics_data = validated_data.pop('topics', [])
        chapter = Topics.objects.create(**validated_data)
        for topic_data in topics_data:
            SubTopics.objects.create(topic=chapter, **topic_data)
        return chapter

    def update(self, instance, validated_data):
        topics_data = validated_data.pop('topics', [])
        instance.name = validated_data.get('name', instance.name)
        instance.subject = validated_data.get('subject', instance.subject)
        instance.save()

        # Update or create topics
        for topic_data in topics_data:
            topic_id = topic_data.get('id')
            if topic_id:
                topic = SubTopics.objects.get(id=topic_id, topic=instance)
                topic.name = topic_data.get('name', topic.name)
                topic.save()
            else:
                SubTopics.objects.create(topic=instance, **topic_data)
        
        return instance
    

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = classes
        fields = ['id' ,'class_name','class_code']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['subject_name','subject_code']

class TopicSerializer(serializers.ModelSerializer):
    # topics = TopicSerializer(many=True)

    class Meta:
        model = Topics
        fields = ['name','subject','topic_code']


class InputSerializer(serializers.Serializer):
    classid = serializers.IntegerField()
    subjectid = serializers.IntegerField()
    topicid = serializers.ListField(allow_empty=True)
    # subtopicid = serializers.ListField(allow_empty=True)
    solved = serializers.BooleanField(required=False)
    exercise = serializers.BooleanField(required=False)
    external = serializers.ChoiceField(choices=['level-1', 'level-2', 'level-3'], required=False, allow_null=True)
    # external = serializers.DictField(required=False, allow_null=True)
# {
#     "class_id": 4,
#     "subjectid": 3,
#     "chapterid": [48],
#     "topicid": [],
#     "solved": true,
#     "exercise": false,
#     "external": null
# }

class StudentSubmitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question_Answers
        fields = '__all__'

    class Meta:
        model = StudentSubmits
        fields = '__all__'

class QuestionWithImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionWithImage
        fields = ['question','question_image']
        
        
class GapAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = GapAnalysis
        fields = '__all__'
        
from myapp.models import Homework,Notification

class HomeworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = ['title', 'description', 'due_date', 'date_assigned', 'attachment', 'homework_code']


class NotificationSerializer(serializers.ModelSerializer):
    homework = HomeworkSerializer()  # nested

    class Meta:
        model = Notification
        fields = ['message', 'homework', 'timestamp']

from .models import HomeworkSubmission

class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkSubmission
        fields = '__all__'