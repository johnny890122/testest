from otree.api import *
import random, json

from otree.models import player

c = Currency

doc = """
PGG version 1.0.0
"""

class Constants(BaseConstants):
	''' oTree 基本設定 '''
	name_in_url = 'PGG_decision'
	players_per_group = 4
	num_rounds = 10

	'''PGG 參數'''
	multiplier = 2
	endowment = 20

	'''「甲」和「乙」的驗證基數'''
	a_role_val_num = 2
	b_role_val_num = 2

	'''跟報酬有關的變數'''
	a_role_payoff = 100
	a_role_bonus = 100
	b_role_payoff = 100
	b_role_bonus = 100
	viewer_guess_bonus = 5

	'''提醒作答的秒數'''
	timeout_seconds = 45
	remind_seconds = 5
	num_quest = 25
	num_quest_need = 20

	width = '850px'
	height = '1.7'

class Subsession(BaseSubsession):
	pass

class Group(BaseGroup):
	# PGG 中該組的總貢獻量
	total_contribution = models.IntegerField()
	# PGG 中個人能分到的小組份額
	individual_share = models.CurrencyField()


class Player(BasePlayer):
	'''跟 treatment 有關的參數'''
	pgg_role = models.StringField()
	id_treatment = models.StringField()
	contri_treatment = models.StringField()
	pgg_id = models.StringField()

	'''跟報酬有關的 treatment '''
	contribution = models.IntegerField(
		label = '',
		min = 0, 
		max = Constants.endowment,
		)

	'''決策時間'''
	decision_duration = models.StringField()
	

	## 給報酬頁面使用
	id_1 = models.StringField()
	id_2 = models.StringField()
	id_3 = models.StringField()
	id_4 = models.StringField()

	contribution_1 = models.IntegerField()
	contribution_2 = models.IntegerField()
	contribution_3 = models.IntegerField()
	contribution_4 = models.IntegerField()

def creating_session(subsession: Subsession):
	for player in subsession.get_players():
		if subsession.round_number == 1:
			player.pgg_role = player.participant.pgg_role
			player.id_treatment = player.participant.id_treatment
			player.contri_treatment = player.participant.contri_treatment
			if player.id_treatment == 'id_sys':
				player.pgg_id = player.participant.pgg_id
		else:
			player.pgg_role = player.in_round(1).pgg_role
			player.id_treatment = player.in_round(1).id_treatment
			player.contri_treatment = player.in_round(1).contri_treatment
			if player.id_treatment == 'id_sys':
				player.pgg_id = player.in_round(1).pgg_id

# 決定 PGG 報酬
def set_payoffs(group: Group):
	players = group.get_players()
	contributions = [p.contribution for p in players]
	group.total_contribution = sum(contributions)
	group.individual_share = (
		group.total_contribution * Constants.multiplier / Constants.players_per_group
	)
	for p in players:
		p.payoff = Constants.endowment - p.contribution + group.individual_share

	##給報酬頁面使用

	id_list = []
	contribution_list = []
	for p in random.sample(players, 4):
		id_list.append(p.participant.pgg_id)
		contribution_list.append(p.contribution)

	for p in players:
		number_list = [0, 1, 2, 3]
		num_1 = random.choice(number_list)
		number_list.remove(num_1)
		num_2 = random.choice(number_list)
		number_list.remove(num_2)
		num_3 = random.choice(number_list)
		number_list.remove(num_3)
		num_4 = random.choice(number_list)
		number_list.remove(num_4)

		p.id_1 = id_list[num_1]
		p.id_2 = id_list[num_2]
		p.id_3 = id_list[num_3]
		p.id_4 = id_list[num_4]

		p.contribution_1 = contribution_list[num_1]
		p.contribution_2 = contribution_list[num_2]
		p.contribution_3 = contribution_list[num_3]
		p.contribution_4 = contribution_list[num_4]


class Arrival_Page_Before_Screen_6(WaitPage):
	template_name = '_templates/global/MyWaitPage.html'

	group_by_arrival_time = True

	title_text = "請等待"
	body_text = "請您耐心等待其他受試者完成第一階段的決策項目後，再一同進入實驗。"

	@staticmethod 
	def is_displayed(player: Player):
		return player.round_number == 1	



# 第二個決策項目 - 決策
class Screen_6(Page):
	form_model = 'player'
	form_fields = ['contribution', 'decision_duration']

	@staticmethod
	def js_vars(player):
		return {
				"timeout_seconds": Constants.timeout_seconds,
				"remind_seconds": Constants.remind_seconds,
		}

	@staticmethod
	def before_next_page(player: Player, timeout_happened):
		player.pgg_id = player.participant.pgg_id

	@staticmethod
	def vars_for_template(player: Player):
		return {
			"pgg_id": player.participant.pgg_id,
		}

# 第二個決策項目 - 等待頁面
class Wait_Page_Before__Screen_7(WaitPage):
	template_name = '_templates/global/MyWaitPage.html'
	title_text = "請等待"
	body_text = "請您耐心等待您的組員。"
	@staticmethod
	def after_all_players_arrive(group: Group):
		set_payoffs(group)


# 第二個決策項目 - 報酬
class Screen_7(Page):
	@staticmethod
	def vars_for_template(player: Player):
		return {
			"player_preserve": Constants.endowment - player.contribution,
			"pgg_id": player.participant.pgg_id,
		}

class Screen_8(Page):
	@staticmethod
	def is_displayed(player: Player):
		return player.round_number == Constants.num_rounds

	@staticmethod
	def vars_for_template(player: Player):
		return {
			"pgg_total_payoff": sum([p.payoff for p in player.in_all_rounds()]),
		}

page_sequence = [Arrival_Page_Before_Screen_6, Screen_6, Wait_Page_Before__Screen_7, Screen_7, Screen_8]

