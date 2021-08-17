from rules import add_perm

from aleksis.core.util.predicates import has_global_perm, has_person, is_site_preference_set

# Show Hjelp menu
show_hjelp_menu = is_site_preference_set("hjelp", "public_faq") | (
    has_person
    & (
        has_global_perm("hjelp.view_faq")
        | has_global_perm("hjelp.ask_faq")
        | has_global_perm("hjelp.report_issue")
        | has_global_perm("hjelp.send_feedback")
    )
)
add_perm("hjelp.show_menu_rule", show_hjelp_menu)

# View FAQ
view_faq_predicate = is_site_preference_set("hjelp", "public_faq") | (
    has_person & has_global_perm("hjelp.view_faq")
)
add_perm("hjelp.view_faq_rule", view_faq_predicate)

# Change FAQ
change_faq_predicate = has_person & (
    has_global_perm("hjelp.change_faqsection") | has_global_perm("hjelp.change_faqquestion")
)
add_perm("hjelp.change_faq_rule", change_faq_predicate)

# Ask FAQ question
ask_faq_predicate = has_person & has_global_perm("hjelp.ask_faq")
add_perm("hjelp.ask_faq_rule", ask_faq_predicate)

# Report issue
report_issue_predicate = has_person & has_global_perm("hjelp.report_issue")
add_perm("hjelp.report_issue_rule", report_issue_predicate)

# Add feedback
send_feedback_predicate = has_person & has_global_perm("hjelp.send_feedback")
add_perm("hjelp.send_feedback_rule", send_feedback_predicate)
