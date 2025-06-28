from rest_framework import serializers
from .models import ACARSMessage


class ACARSMessageSerializer(serializers.ModelSerializer):
    """
    Serializer dla modelu ACARSMessage
    Automatycznie przypisuje użytkownika na podstawie uwierzytelnionego użytkownika
    """
    
    class Meta:
        model = ACARSMessage
        fields = '__all__'
        read_only_fields = ('user', 'timestamp')
        
    def create(self, validated_data):
        """
        Tworzy nową wiadomość ACARS z automatycznym przypisaniem użytkownika
        """
        # Użytkownik jest automatycznie przypisywany w widoku
        return super().create(validated_data)


class ACARSMessageReadSerializer(serializers.ModelSerializer):
    """
    Serializer tylko do odczytu z dodatkowymi informacjami o użytkowniku
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = ACARSMessage
        fields = '__all__' 