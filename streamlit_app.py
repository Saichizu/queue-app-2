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
        st.session_state.pinged = set(data.get("pinged", []))
    else:
        st.session_state.queue = []
        st.session_state.calypso = []
        st.session_state.pinged = set()

def save_state():
    data = {
        "queue": st.session_state.queue,
        "calypso": st.session_state.calypso,
        "pinged": list(st.session_state.pinged)
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

# Input box + Join button in same row
def join_on_enter():
    name = st.session_state.name_input.strip()
    if name and name not in st.session_state.queue and name not in st.session_state.calypso:
        st.session_state.queue.append(name)
        st.session_state.name_input = ""  # clear input
        save_state()
        st.session_state.rev += 1
        st.session_state.needs_rerun = True

# Two columns: input (wide) + button (narrow)
col1, col2 = st.columns([4,1])
with col1:
    st.text_input(
        "Add to Queue:",
        key="name_input",
        on_change=join_on_enter,
        label_visibility="collapsed"  # hides the "Add to Queue:" label
    )
with col2:
    st.button("🎤 Join", on_click=join_on_enter, use_container_width=True)

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
        st.session_state.pinged.clear()
        bump_and_rerun()
with cols[2]:
    st.write(" ")  # spacer

# ---- Quick Actions (tight 2-column layout) ----
st.markdown("#### Quick Actions")
qa = st.columns(4)  # now 4 actions (Leave, Hold, Return, Ping)

# Init flags
for flag in ["show_leave", "show_hold", "show_return", "show_ping"]:
    if flag not in st.session_state:
        st.session_state[flag] = False

# CSS for compact name buttons
st.markdown("""
    <style>
    .name-btn button {
        font-size: clamp(8px, 1.2vw, 12px) !important;  /* auto shrink, min 8px */
        padding: 6px 8px !important;
        margin: 2px !important;
        border-radius: 10px !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 6px !important;  /* tighten columns */
    }
    div[data-testid="stVerticalBlock"] {
        gap: 4px !important;  /* tighten rows */
    }
    </style>
""", unsafe_allow_html=True)

def render_names(names, action_key):
    cols = st.columns(2, gap="small")
    for i, person in enumerate(names):
        col = cols[i % 2]
        with col:
            st.markdown('<div class="name-btn">', unsafe_allow_html=True)
            if st.button(person, key=f"{action_key}_{i}", use_container_width=True):
                return person
            st.markdown('</div>', unsafe_allow_html=True)
    return None


with qa[0]:
    if st.button("➖ Leave", use_container_width=True):
        st.session_state.show_leave = not st.session_state.show_leave
        st.session_state.show_hold = False
        st.session_state.show_return = False
        st.session_state.show_ping = False

    if st.session_state.show_leave:
        person = render_names(st.session_state.queue, "Leave")
        if person:
            st.session_state.queue.remove(person)
            st.session_state.pinged.discard(person)
            bump_and_rerun()

with qa[1]:
    if st.button("⏳ Hold", use_container_width=True):
        st.session_state.show_hold = not st.session_state.show_hold
        st.session_state.show_leave = False
        st.session_state.show_return = False
        st.session_state.show_ping = False

    if st.session_state.show_hold:
        person = render_names(st.session_state.queue, "Hold")
        if person:
            st.session_state.queue.remove(person)
            st.session_state.calypso.append(person)
            bump_and_rerun()

with qa[2]:
    if st.button("🏝️ Return", use_container_width=True):
        st.session_state.show_return = not st.session_state.show_return
        st.session_state.show_leave = False
        st.session_state.show_hold = False
        st.session_state.show_ping = False

    if st.session_state.show_return:
        person = render_names(st.session_state.calypso, "↩️")
        if person:
            st.session_state.calypso.remove(person)
            st.session_state.queue.append(person)
            bump_and_rerun()

with qa[3]:
    if st.button("📣 Ping/Unping", use_container_width=True):
        st.session_state.show_ping = not st.session_state.show_ping
        st.session_state.show_leave = False
        st.session_state.show_hold = False
        st.session_state.show_return = False

    if st.session_state.show_ping:
        names = st.session_state.queue + st.session_state.calypso
        person = render_names(names, "📣")
        if person:
            if person in st.session_state.pinged:
                st.session_state.pinged.remove(person)
            else:
                st.session_state.pinged.add(person)
            bump_and_rerun()

# ---- Layout: Reorder (left) + Output (right) ----
if st.session_state.queue:
    st.markdown("### Queue Manager")

    left, right = st.columns([1, 2])

    with left:
        st.markdown("#### 🔀 Reorder")
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
        def fmt_name(name):
            return f"{name} 📣" if name in st.session_state.pinged else name

        output = "🏛️ 𝑬𝑷𝑰𝑪 𝑺𝒐𝒏𝒈 𝑸𝒖𝒆𝒖𝒆 2 🎭\n"
        output += ("━━━━━━━━━━━━━━━━━━━━━\n"
                   "🎶 𝑪𝑼𝑹𝑹𝑬𝑵𝑻𝑳𝒀 𝑺𝑰𝑵𝑮𝑰𝑵𝑮\n"
                   f"✨👑🎤 {fmt_name(st.session_state.queue[0]) if len(st.session_state.queue) >= 1 else '-'}\n")
        output += ("━━━━━━━━━━━━━━━━━━━━━\n"
                   "⏭️ 𝑵𝑬𝑿𝑻 𝑼𝑷\n"
                   f"🌟 {fmt_name(st.session_state.queue[1]) if len(st.session_state.queue) >= 2 else '-'}\n")
        output += "━━━━━━━━━━━━━━━━━━━━━\n"
        output += "🛶 𝑶𝑵 𝑸𝑼𝑬𝑼𝑬\n"
        if len(st.session_state.queue) > 2:
            for person in st.session_state.queue[2:]:
                output += f"🎭 {fmt_name(person)}\n"
        else:
            output += "- None\n"
        output += "━━━━━━━━━━━━━━━━━━━━━\n"
        output += "🏝️ 𝑨𝒘𝒂𝒚 𝒘𝒊𝒕𝒉 𝑪𝒂𝒍𝒚𝒑𝒔𝒐\n"
        if st.session_state.calypso:
            for person in st.session_state.calypso:
                output += f"🌴 {fmt_name(person)}\n"
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

        st.code(output, language="text")

# Always save state at end of render
save_state()

# Force rerun after input enter (fixes reorder not refreshing)
if st.session_state.get("needs_rerun"):
    st.session_state.needs_rerun = False
    st.rerun()











