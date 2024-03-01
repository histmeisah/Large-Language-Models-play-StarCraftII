class Template:
    def __init__(self):
        # 这里只定义一个输入模板，您可以根据需要增加其他模板或条件逻辑。
        self.input_template_v1 = self.get_input_template_v1()
        self.input_template_v2 = self.get_input_template_v2()
        self.input_template_v3 = self.get_input_template_v3()
    def get_input_template_v1(self):
        # 使用占位符 {chunks_str}
        return """
    --- StarCraft II Game Summary ---
    Description: This section primarily records and summarizes our observations from the first {num_rounds} rounds.
    Details:
    {chunks_str}
    """
    def get_input_template_v2(self):
        # 使用占位符 {chunks_str}, {executed_actions_str} 和 {failed_actions_str}
        return """
    --- StarCraft II Game Summary ---
    Description: This section primarily records and summarizes our observations from the first {num_rounds} rounds.
    Details:
    {chunks_str}

    --- Executed Actions ---
    Description: This section primarily records the actions we have already executed, starting from the earliest to the most recent.
    Details:
    {executed_actions_str}

    --- Failed Actions [IMPORTANT] ---
    Description: This section primarily records the actions that failed and the corresponding reasons, starting from the earliest to the most recent.
    Details:
    {failed_actions_str}
    """

    def get_input_template_v3(self):
        return """
        --- StarCraft II Game Summary ---
        Description: This section primarily records and summarizes our observations from the first {num_rounds} rounds.

        --- Key Categories ---
        - Resource: Represents the basic resources available, such as minerals and vespene gas.
        - Building: Details about various structures, from production buildings to defensive structures.
        - Unit: Information about various combat and non-combat units, including their types and quantities.
        - Planning: Insights into planning structures and units, detailing our strategic planning for upcoming rounds.
        - Research: Highlights advancements and upgrades researched from different buildings like the cybernetics core, forge, etc.
        - Enemy: Observations about enemy units and structures, helping in understanding enemy tactics and strategies.

        Details:
        {chunks_str}
        """


