from rest_framework import serializers
from gestionaircontrol.callcenter.models import Player, Answer
from gestionaircontrol.wheel.models import Prize


class PlayerAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('sequence', 'correct', 'answer')

    def to_representation(self, instance):
        ret = super(serializers.ModelSerializer, self).to_representation(instance)
        translation = instance.question
        ret['question'] = translation.question.number
        ret['code'] = translation.language.code
        ret['duration'] = 0
        if instance.hangup_time is not None and instance.pickup_time is not None:
            ret['duration'] = (instance.hangup_time - instance.pickup_time).total_seconds()

        return ret


class GamePlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('name', 'score', 'answers')

    answers = PlayerAnswerSerializer(many=True, read_only=True)


class PrizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prize
        fields = ('name', 'percentage', 'stock', 'big', 'free')
