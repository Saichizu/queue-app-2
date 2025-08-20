import streamlit as st
import streamlit_sortables as sortables
import json, os

# ---------------- Persistence ----------------
SAVE_FILE = "queue.json"

def load_state():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        st.session_state.queue = data.get("queue", [])
        st.session_state.calypso = data.get("calypso", [])
    else:
        st.session_state.queue = []
        st.session_state.calypso = []

def save_state():
    data = {
        "queue": st.session_state.queue,
        "calypso": st.session_state.calypso
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

# ---------------- Init ----------------
if "initialized" not in st.session_state:
    load_state()
    st.session_state.rev = 0
    st.session_state.initialized = True

def bump_and_rerun():
    save_state()
    st.session_state.rev += 1
    st.rerun()

# ---------------- UI ----------------
st.title("⚔️EPIC Song Queue 2🎭")

# Input box (Enter = Join)
def join_on_enter():
    name = st.session_state.name_input.strip()
    if name and name not in st.session_state.queue and name not in st.session_state.calypso:
        st.session_state.queue.append(name)
        st.session_state.name_input = ""  # clear input
        save_state()
        # bump rev so sortable remounts on next render
        st.session_state.rev += 1
        st.session_state.needs_rerun = True



st.text_input(
    "Add to Queue:",
    key="name_input",
    on_change=join_on_enter
)

# --- Top button bar ---
cols = st.columns(3)
with cols[0]:
    if st.button("⏩ Advance", use_container_width=True):
        if st.session_state.queue:
            first = st.session_state.queue.pop(0)
            st.session_state.queue.append(first)
            bump_and_rerun()
with cols[1]:
    if st.button("🧹 Clear All", use_container_width=True):
        st.session_state.queue.clear()
        st.session_state.calypso.clear()
        bump_and_rerun()
with cols[2]:
    st.write(" ")  # spacer

# ---- Quick Actions (compact like reorder) ----
st.markdown("#### Quick Actions")
qa = st.columns(3)

# Init flags
for flag in ["show_leave", "show_hold", "show_return"]:
    if flag not in st.session_state:
        st.session_state[flag] = False

with qa[0]:
    if st.button("➖ Leave", use_container_width=True):
        st.session_state.show_leave = not st.session_state.show_leave
        st.session_state.show_hold = False
        st.session_state.show_return = False

    if st.session_state.show_leave:
        if not st.session_state.queue:
            st.caption("— No one in queue —")
        else:
            st.markdown("##### Click a name to Leave:")
            for i, person in enumerate(st.session_state.queue):
                if st.button(f"❌ {person}", key=f"leave_btn_{i}"):
                    st.session_state.queue.remove(person)
                    bump_and_rerun()

with qa[1]:
    if st.button("⏳ Hold", use_container_width=True):
        st.session_state.show_hold = not st.session_state.show_hold
        st.session_state.show_leave = False
        st.session_state.show_return = False

    if st.session_state.show_hold:
        if not st.session_state.queue:
            st.caption("— No one in queue —")
        else:
            st.markdown("##### Click a name to Hold:")
            for i, person in enumerate(st.session_state.queue):
                if st.button(f"⏳ {person}", key=f"hold_btn_{i}"):
                    st.session_state.queue.remove(person)
                    st.session_state.calypso.append(person)
                    bump_and_rerun()

with qa[2]:
    if st.button("🏝️ Return", use_container_width=True):
        st.session_state.show_return = not st.session_state.show_return
        st.session_state.show_leave = False
        st.session_state.show_hold = False

    if st.session_state.show_return:
        if not st.session_state.calypso:
            st.caption("— No one away —")
        else:
            st.markdown("##### Click a name to Return:")
            for i, person in enumerate(st.session_state.calypso):
                if st.button(f"↩️ {person}", key=f"return_btn_{i}"):
                    st.session_state.calypso.remove(person)
                    st.session_state.queue.append(person)
                    bump_and_rerun()





# ---- Layout: Reorder (left) + Output (right) ----
if st.session_state.queue:
    st.markdown("### Queue Manager")

    left, right = st.columns([1, 2])  # left smaller, right bigger

    with left:
        st.markdown("#### 🔀 Reorder")
        # Use only names (no numbering)
        reordered = sortables.sort_items(
            st.session_state.queue,
            direction="vertical",
            key=f"sortable_{st.session_state.rev}"
        )
        if reordered != st.session_state.queue:
            st.session_state.queue = reordered
            st.session_state.rev += 1
            save_state()
            st.rerun()

    with right:
        # ---- Build final output ----
        output = "🏛️ 𝑬𝑷𝑰𝑪 𝑺𝒐𝒏𝒈 𝑸𝒖𝒆𝒖𝒆 2 🎭\n"
        output += ("━━━━━━━━━━━━━━━━━━━━━\n"
                   "🎶 𝑪𝑼𝑹𝑹𝑬𝑵𝑻𝑳𝒀 𝑺𝑰𝑵𝑮𝑰𝑵𝑮\n"
                   f"✨👑🎤 {st.session_state.queue[0] if len(st.session_state.queue) >= 1 else '-'}\n")
        output += ("━━━━━━━━━━━━━━━━━━━━━\n"
                   "⏭️ 𝑵𝑬𝑿𝑻 𝑼𝑷\n"
                   f"🌟 {st.session_state.queue[1] if len(st.session_state.queue) >= 2 else '-'}\n")
        output += "━━━━━━━━━━━━━━━━━━━━━\n"
        output += "🛶 𝑶𝑵 𝑸𝑼𝑬𝑼𝑬\n"
        if len(st.session_state.queue) > 2:
            for person in st.session_state.queue[2:]:
                output += f"🎭 {person}\n"
        else:
            output += "- None\n"
        output += "━━━━━━━━━━━━━━━━━━━━━\n"
        output += "🏝️ 𝑨𝒘𝒂𝒚 𝒘𝒊𝒕𝒉 𝑪𝒂𝒍𝒚𝒑𝒔𝒐\n"
        if st.session_state.calypso:
            for person in st.session_state.calypso:
                output += f"🌴 {person}\n"
        else:
            output += "- None\n"
        output += ("━━━━━━━━━━━━━━━━━━━━━\n"
                   "React to join the legend:\n"
                   "🎤 — Join the Queue\n"
                   "🚪 — Leave the Queue\n"
                   "📣 — Summon the Bard (Ping)\n"
                   "⏳ — Place Me On Hold\n"
                   "━━━━━━━━━━━━━━━━━━━━━\n")
        output += "by Saichizu :)"

        # Main display + built-in copy button
        st.code(output, language="text")


# Always save state at end of render
save_state()

# Force rerun after input enter (fixes reorder not refreshing)
if st.session_state.get("needs_rerun"):
    st.session_state.needs_rerun = False
    st.rerun()




















