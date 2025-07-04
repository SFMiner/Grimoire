# 🧙‍♂️ Grimoire Language Support for VS Code

**The ultimate VSCode extension for the revolutionary Grimoire magical programming language!**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://marketplace.visualstudio.com/items?itemName=grimoire-lang.grimoire-language)
[![Downloads](https://img.shields.io/badge/downloads-0+-brightgreen.svg)](https://marketplace.visualstudio.com/items?itemName=grimoire-lang.grimoire-language)

## ✨ **Revolutionary Features**

### 🎭 **Intelligent Thematic Keyword Suggestions**
**World's first language extension with magical keyword variants!**

When you type `bind`, see magical alternatives appear:
- **✨ Light Magic**: `bless`, `consecrate`, `sanctify`
- **🌑 Shadow Magic**: `curse`, `hex`, `doom`  
- **🔮 Arcane Magic**: `inscribe`, `encode`, `cipher`
- **🌿 Nature Magic**: `grow`, `cultivate`, `nurture`
- **⭐ Divine Magic**: `ordain`, `decree`, `proclaim`
- **🎭 Trickster Magic**: `trick`, `swap`, `transform`

![Thematic Suggestions Demo](demo-suggestions.gif)

### 🎨 **Magic School Syntax Highlighting**
Each magic school gets its own beautiful colors:
- **✨ Gold** for Light Magic keywords
- **🌑 Purple** for Shadow Magic keywords  
- **🔮 Blue** for Arcane Magic keywords
- **🌿 Green** for Nature Magic keywords
- **⭐ Sky Blue** for Divine Magic keywords
- **🎭 Orange** for Trickster Magic keywords

### 🔮 **Smart Hover Information**
Hover over any keyword to see:
- **Current magic school** and theme
- **Alternative variants** from other schools
- **Usage suggestions** for thematic consistency

### 🧙‍♂️ **Advanced IntelliSense**
- **Context-aware completions** for all magic schools
- **Emoji-enhanced suggestions** for easy identification
- **Instant keyword replacement** with right-click menu

## 🚀 **Installation**

1. **Install from VS Code Marketplace**:
   - Open VS Code
   - Go to Extensions (`Ctrl+Shift+X`)
   - Search for "Grimoire Language Support"
   - Click Install

2. **Manual Installation**:
   ```bash
   # Clone the extension
   git clone https://github.com/SFMiner/Grimoire
   cd Grimoire/vscode-extension
   
   # Install dependencies
   npm install
   
   # Compile TypeScript
   npm run compile
   
   # Package extension
   npm run package
   ```

## 🎭 **Usage Examples**

### **Basic Keyword Suggestions**
```grimoire
# Type "bind" and see magical alternatives:
bind health = 100        # ⚡ Neutral Magic
bless health = 100       # ✨ Light Magic  
curse health = 100       # 🌑 Shadow Magic
inscribe health = 100    # 🔮 Arcane Magic
```

### **Thematic Code Styles**

**🏥 Healing Game (Light Magic):**
```grimoire
blessing heal_player():
    bless player_health = 75
    should blessed player_health is lesser than 100:
        empower player_health by 25
        illuminate $SCROLL(✨ Divine light restores you!)
    lest darkened:
        reveal $SCROLL(💫 You are at full health!)
```

**👹 Horror Game (Shadow Magic):**
```grimoire
curse drain_soul():
    hex victim_energy = 50
    should cursed victim_energy is greater than 0:
        weaken victim_energy by 20
        whisper $SCROLL(🌑 Dark energy drains your essence...)
    lest blessed:
        materialize $SCROLL(💀 Nothing left to drain...)
```

**🚀 Sci-Fi Game (Arcane Magic):**
```grimoire
formula calculate_trajectory():
    inscribe velocity = 299792458
    should logical velocity is greater than 0:
        amplify velocity by 1000
        divine $SCROLL(🔮 Quantum calculations complete!)
    lest illogical:
        compute $SCROLL(❌ Physics violation detected!)
```

## 🎨 **Theme Support**

### **🌑 Grimoire Dark Magic Theme**
Perfect for late-night magical coding sessions:
- **Dark mystical background** with deep blues and purples
- **Color-coded magic schools** for instant recognition
- **Optimized contrast** for extended coding

### **✨ Grimoire Light Magic Theme**  
Bright and magical for daytime development:
- **Clean light background** with subtle mystical touches
- **Vibrant magic school colors** that pop
- **Easy on the eyes** for long development sessions

## ⌨️ **Keyboard Shortcuts**

| Command | Shortcut | Description |
|---------|----------|-------------|
| **Show Keyword Variants** | `Ctrl+Shift+K` | Display all thematic alternatives for selected keyword |
| **Convert to Magic School** | `Ctrl+Shift+M` | Quick-convert selected text to different magic school |
| **Toggle Grimoire Theme** | `Ctrl+Shift+T` | Switch between Dark/Light magic themes |

## 🔧 **Configuration**

Add these settings to your VS Code `settings.json`:

```json
{
  "grimoire.enableThematicSuggestions": true,
  "grimoire.defaultMagicSchool": "neutral",
  "grimoire.showEmojiInSuggestions": true,
  "grimoire.enableHoverHelp": true,
  "grimoire.autoSuggestVariants": true
}
```

## 📁 **File Extensions**

The extension automatically activates for:
- **`.grim`** files (recommended)
- **`.grimoire`** files

## 🎯 **Commands**

Access via Command Palette (`Ctrl+Shift+P`):

- **`Grimoire: Show Keyword Variants`** - Display thematic alternatives
- **`Grimoire: Convert to Magic School`** - Transform code style
- **`Grimoire: Generate Example Code`** - Create sample magical programs
- **`Grimoire: Toggle Magic Theme`** - Switch visual themes

## 🧪 **Features in Action**

### **🎭 Intelligent Autocomplete**
1. Type any Grimoire keyword
2. **Instantly see** thematic alternatives with magic school icons
3. **Choose your style** - Light Magic for healing, Shadow for horror, etc.
4. **Consistent theming** throughout your magical codebase

### **🔮 Context-Aware Assistance**
- **Hover information** shows all alternative keywords
- **Right-click menu** for instant keyword conversion  
- **Smart suggestions** based on surrounding code context
- **Magic school consistency** warnings and suggestions

### **✨ Beautiful Syntax Highlighting**
- **Each magic school** gets distinctive colors
- **$SCROLL()** strings highlighted as magical scrolls
- **Operators** like `should`/`lest` get special treatment
- **Function calls** with `upon` syntax beautifully styled

## 🌟 **Why This Extension?**

### **🎭 Revolutionary Language Support**
This is the **world's first programming language** with comprehensive thematic keyword variants. Your extension provides:

- **Infinite creative expression** - same logic, unlimited styles
- **Perfect for game development** - match keywords to game atmosphere  
- **Educational tool** - learn programming through preferred themes
- **Artistic coding** - where programming meets creative writing

### **🧙‍♂️ Magical Development Experience**
Transform mundane programming into **spellcasting**:
- Code **feels like writing magical incantations**
- **Thematic consistency** makes code more immersive
- **Visual beauty** with color-coded magic schools
- **Intelligent assistance** that understands your magical intent

## 📖 **Language Reference**

### **Magic Schools Overview:**

| School | Theme | Example Keywords | Best For |
|--------|-------|------------------|----------|
| **✨ Light** | Healing, Protection | `bless`, `illuminate`, `blessing` | RPGs, healing systems |
| **🌑 Shadow** | Dark Arts, Curses | `curse`, `whisper`, `hex` | Horror, dark magic |
| **🔮 Arcane** | Knowledge, Logic | `inscribe`, `divine`, `formula` | Sci-fi, calculations |
| **🌿 Nature** | Elements, Life | `grow`, `sing`, `nurture` | Nature magic, growth |
| **⭐ Divine** | Holy Power | `ordain`, `prophesy`, `miracle` | Religious themes |
| **🎭 Trickster** | Chaos, Change | `trick`, `jest`, `transform` | Comedy, randomness |

## 🐛 **Known Issues**

- **Multi-line REPL**: Complex constructs work better in files than REPL
- **Performance**: Large files with many variants may have slight delays
- **Theme conflicts**: May override other language themes temporarily

## 🔄 **Changelog**

### **v1.0.0** - Initial Release
- ✨ **Thematic keyword suggestions** with 7 magic schools
- 🎨 **Beautiful syntax highlighting** with school-specific colors
- 🔮 **Smart hover information** showing alternatives
- 🧙‍♂️ **Two magical themes** (Dark Magic & Light Magic)
- ⌨️ **Keyboard shortcuts** and commands
- 📖 **Comprehensive language support**

## 🤝 **Contributing**

We welcome contributions to make Grimoire even more magical!

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin amazing-feature`
5. **Open a Pull Request**

## 📄 **License**

This extension is released under the **MIT License**.

## 🎉 **Credits**

Created with ✨ for the **Grimoire Programming Language** - where programming meets magic!

- **Language Design**: Revolutionary thematic keyword variants system
- **Extension Development**: Advanced IntelliSense and theming
- **Community**: Magical developers worldwide

---

**🧙‍♂️ Start your magical programming journey today!**

*Transform your code from mundane syntax into mystical incantations with the power of thematic keyword variants!*