import smartchoices


class AssociationChoices(smartchoices.Choices):
    """An enum for the various supported associations."""
    WFTDA = smartchoices.Choice()
    MRDA = smartchoices.Choice()
    JRDA = smartchoices.Choice()

    OTHER = smartchoices.Choice(99)


class GameTypeChoices(smartchoices.Choices):
    """An enum for the various game types."""
    SANCTIONED = smartchoices.Choice()
    REGULATION = smartchoices.Choice()

    OTHER = smartchoices.Choice(99)


class OfficialPositions(smartchoices.Choices):
    """An enum for official positions."""
    class Meta:
        smart_names = True

    HEAD_REF = smartchoices.Choice()
    INSIDE_PACK_REF = smartchoices.Choice()
    JAM_REF = smartchoices.Choice()
    OUTSIDE_PACK_REF = smartchoices.Choice()
    ALT = smartchoices.Choice()

    HEAD_NSO = smartchoices.Choice()
    PENALTY_TRACKER = smartchoices.Choice()
    PENALTY_WRANGLER = smartchoices.Choice()
    INSIDE_WHITEBOARD = smartchoices.Choice()
    JAM_TIMER = smartchoices.Choice()
    SCORE_KEEPER = smartchoices.Choice()
    SCOREBOARD_OPERATOR = smartchoices.Choice()
    PENALTY_BOX_MANAGER = smartchoices.Choice()
    PENALTY_BOX_TIMER = smartchoices.Choice()
    LINEUP_TRACKER = smartchoices.Choice()
    ALT1 = smartchoices.Choice()
    ALT2 = smartchoices.Choice()


class SkatingPositions(smartchoices.Choices):
    """An enum for skating official positions."""
    class Meta:
        smart_names = True
    HEAD_REF = smartchoices.Choice()
    INSIDE_PACK_REF = smartchoices.Choice()
    JAM_REF = smartchoices.Choice()
    OUTSIDE_PACK_REF = smartchoices.Choice()
    ALT = smartchoices.Choice()


class NonskatingPositions(smartchoices.Choices):
    """An enum for non-skating official positions."""
    class Meta:
        smart_names = True
    JAM_TIMER = smartchoices.Choice()
    SCORE_KEEPER = smartchoices.Choice()
    PENALTY_BOX_MANAGER = smartchoices.Choice()
    PENALTY_BOX_TIMER = smartchoices.Choice()
    PENALTY_TRACKER = smartchoices.Choice()
    PENALTY_WRANGLER = smartchoices.Choice()
    INSIDE_WHITEBOARD = smartchoices.Choice()
    LINEUP_TRACKER = smartchoices.Choice()
    SCOREBOARD_OPERATOR = smartchoices.Choice()


class OfficialType(smartchoices.Choices):
    """An enum for official types."""
    class Meta:
        smart_names = True
    ALL = smartchoices.Choice()
    SKATING = smartchoices.Choice()
    NONSKATING = smartchoices.Choice()
