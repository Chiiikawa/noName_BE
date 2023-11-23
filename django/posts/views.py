from rest_framework import viewsets
from .models import Post, Like, Comment, GeneratedImage
from .serializers import LikeSerializer, CommentSerializer
from .dalle import generate_image
from rest_framework.views import APIView
from rest_framework.response import Response


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
class DalleAPIView(APIView):
    def post(self, request, *args, **kwargs):
        prompt = request.data.get('prompt') # 클라이언트 요청에서 prompt라는 데이터를 가져옴, prompt는 사용자가 입력한 텍스트 prompt, 이미지 생성에 사용함.
        if not prompt:  # prompt가 비어있거나 없는 경우를 확인함.
            return Response({"error": "No prompt provided"}, status=400)

        image_url = generate_image(prompt)  # generate_image 함수를 호출하여 입력된 prompt를 바탕으로 이미지를 생성하고, 생성된 이미지 URL을 image_url 변수에 저장.

        # 생성된 이미지 정보를 데이터베이스에 저장
        generated_image = GeneratedImage(prompt=prompt, image_url=image_url)    # GeneratedImage 모델 인스턴스를 생성함, 생성된 이미지의 prompt와 url을 저장함.
        generated_image.save()
        return Response({"image": str(image_url)})