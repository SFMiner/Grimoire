import * as vscode from 'vscode';

// Thematic keyword variants mapping
const MAGIC_SCHOOLS = {
    NEUTRAL: {
        name: "Neutral Magic",
        icon: "⚡",
        color: "#888888"
    },
    LIGHT: {
        name: "Light Magic",
        icon: "✨",
        color: "#FFD700"
    },
    SHADOW: {
        name: "Shadow Magic", 
        icon: "🌑",
        color: "#8B008B"
    },
    NATURE: {
        name: "Nature Magic",
        icon: "🌿",
        color: "#228B22"
    },
    DIVINE: {
        name: "Divine Magic",
        icon: "⭐",
        color: "#87CEEB"
    },
    ARCANE: {
        name: "Arcane Magic",
        icon: "🔮",
        color: "#4169E1"
    },
    TRICKSTER: {
        name: "Trickster Magic",
        icon: "🎭",
        color: "#FF6347"
    }
};

const KEYWORD_VARIANTS = {
    // Variable assignment
    'bind': {
        NEUTRAL: ['bind', 'set', 'assign'],
        LIGHT: ['bless', 'consecrate', 'sanctify'],
        SHADOW: ['curse', 'hex', 'doom'],
        NATURE: ['grow', 'cultivate', 'nurture'],
        DIVINE: ['ordain', 'decree', 'proclaim'],
        ARCANE: ['inscribe', 'encode', 'cipher'],
        TRICKSTER: ['trick', 'swap', 'transform']
    },
    
    // Output/printing
    'scry': {
        NEUTRAL: ['scry', 'display', 'show'],
        LIGHT: ['illuminate', 'reveal', 'enlighten'],
        SHADOW: ['whisper', 'manifest', 'materialize'],
        NATURE: ['sing', 'echo', 'resonate'],
        DIVINE: ['prophesy', 'proclaim', 'herald'],
        ARCANE: ['divine', 'calculate', 'compute'],
        TRICKSTER: ['announce', 'jest', 'mock']
    },
    
    // Function definition
    'ritual': {
        NEUTRAL: ['ritual', 'spell', 'procedure'],
        LIGHT: ['blessing', 'prayer', 'invocation'],
        SHADOW: ['curse', 'incantation', 'dark_ritual'],
        NATURE: ['song', 'growth', 'cycle'],
        DIVINE: ['miracle', 'commandment', 'decree'],
        ARCANE: ['formula', 'theorem', 'algorithm'],
        TRICKSTER: ['prank', 'trick', 'jest']
    },
    
    // Object creation
    'conjure': {
        NEUTRAL: ['conjure', 'create', 'make'],
        LIGHT: ['summon', 'call forth', 'manifest'],
        SHADOW: ['raise', 'spawn', 'birth'],
        NATURE: ['sprout', 'bloom', 'emerge'],
        DIVINE: ['create', 'forge', 'craft'],
        ARCANE: ['instantiate', 'construct', 'compile'],
        TRICKSTER: ['poof', 'materialize', 'surprise']
    },
    
    // Class definition
    'artifact': {
        NEUTRAL: ['artifact', 'class', 'blueprint'],
        LIGHT: ['relic', 'sacred object', 'holy vessel'],
        SHADOW: ['cursed item', 'dark relic', 'forbidden tome'],
        NATURE: ['creature', 'being', 'spirit'],
        DIVINE: ['creation', 'vessel', 'avatar'],
        ARCANE: ['construct', 'schema', 'pattern'],
        TRICKSTER: ['disguise', 'illusion', 'form']
    },
    
    // Conditionals
    'should': {
        NEUTRAL: ['should', 'if', 'when'],
        LIGHT: ['should', 'if blessed', 'when pure'],
        SHADOW: ['should', 'if cursed', 'when dark'],
        NATURE: ['should', 'if flourishing', 'when alive'],
        DIVINE: ['should', 'if ordained', 'when holy'],
        ARCANE: ['should', 'if logical', 'when proven'],
        TRICKSTER: ['should', 'if amusing', 'when clever']
    },
    
    'lest': {
        NEUTRAL: ['lest', 'else', 'otherwise'],
        LIGHT: ['lest', 'else darkened', 'otherwise fallen'],
        SHADOW: ['lest', 'else blessed', 'otherwise pure'],
        NATURE: ['lest', 'else withered', 'otherwise dead'],
        DIVINE: ['lest', 'else forsaken', 'otherwise profane'],
        ARCANE: ['lest', 'else illogical', 'otherwise error'],
        TRICKSTER: ['lest', 'else boring', 'otherwise obvious']
    }
};

// Create reverse lookup for all keywords
const ALL_KEYWORDS = new Set<string>();
Object.values(KEYWORD_VARIANTS).forEach(variants => {
    Object.values(variants).forEach((keywords: string[]) => {
        keywords.forEach(keyword => ALL_KEYWORDS.add(keyword));
    });
});

class GrimoireCompletionProvider implements vscode.CompletionItemProvider {
    
    provideCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken,
        context: vscode.CompletionContext
    ): vscode.CompletionItem[] {
        
        const lineText = document.lineAt(position).text;
        const linePrefix = lineText.substr(0, position.character);
        
        // Get the current word being typed
        const wordMatch = linePrefix.match(/(\w+)$/);
        if (!wordMatch) {
            return [];
        }
        
        const currentWord = wordMatch[1].toLowerCase();
        const completions: vscode.CompletionItem[] = [];
        
        // Check if current word matches any base keyword
        for (const [baseKeyword, variants] of Object.entries(KEYWORD_VARIANTS)) {
            if (baseKeyword.startsWith(currentWord) || currentWord === baseKeyword) {
                // Add thematic variants
                for (const [school, keywords] of Object.entries(variants)) {
                    const schoolInfo = MAGIC_SCHOOLS[school as keyof typeof MAGIC_SCHOOLS];
                    
                    keywords.forEach(keyword => {
                        const item = new vscode.CompletionItem(keyword, vscode.CompletionItemKind.Keyword);
                        item.detail = `${schoolInfo.icon} ${schoolInfo.name}`;
                        item.documentation = new vscode.MarkdownString(
                            `**${schoolInfo.name}** variant of \`${baseKeyword}\`\n\n` +
                            `Use this for ${schoolInfo.name.toLowerCase()} themed spells and incantations.`
                        );
                        item.insertText = keyword;
                        item.sortText = `${school}_${keyword}`;
                        
                        // Add color-coded label
                        const label = `${schoolInfo.icon} ${keyword}`;
                        item.label = label;
                        
                        completions.push(item);
                    });
                }
            }
        }
        
        // Also check if typing any variant keyword
        ALL_KEYWORDS.forEach(keyword => {
            if (keyword.startsWith(currentWord) && keyword !== currentWord) {
                // Find which concept this belongs to
                for (const [baseKeyword, variants] of Object.entries(KEYWORD_VARIANTS)) {
                    for (const [school, keywords] of Object.entries(variants)) {
                        if (keywords.includes(keyword)) {
                            const schoolInfo = MAGIC_SCHOOLS[school as keyof typeof MAGIC_SCHOOLS];
                            const item = new vscode.CompletionItem(keyword, vscode.CompletionItemKind.Keyword);
                            item.detail = `${schoolInfo.icon} ${schoolInfo.name}`;
                            item.documentation = new vscode.MarkdownString(
                                `**${schoolInfo.name}** variant of \`${baseKeyword}\``
                            );
                            item.insertText = keyword;
                            item.label = `${schoolInfo.icon} ${keyword}`;
                            completions.push(item);
                            return;
                        }
                    }
                }
            }
        });
        
        return completions;
    }
}

class GrimoireHoverProvider implements vscode.HoverProvider {
    
    provideHover(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken
    ): vscode.Hover | null {
        
        const wordRange = document.getWordRangeAtPosition(position);
        if (!wordRange) {
            return null;
        }
        
        const word = document.getText(wordRange).toLowerCase();
        
        // Check if this word is a thematic variant
        for (const [baseKeyword, variants] of Object.entries(KEYWORD_VARIANTS)) {
            for (const [school, keywords] of Object.entries(variants)) {
                if (keywords.includes(word)) {
                    const schoolInfo = MAGIC_SCHOOLS[school as keyof typeof MAGIC_SCHOOLS];
                    
                    const markdown = new vscode.MarkdownString();
                    markdown.appendMarkdown(`## ${schoolInfo.icon} ${schoolInfo.name} Keyword\n\n`);
                    markdown.appendMarkdown(`**\`${word}\`** is a ${schoolInfo.name.toLowerCase()} variant of \`${baseKeyword}\`\n\n`);
                    markdown.appendMarkdown(`### Other ${schoolInfo.name} variants:\n`);
                    keywords.forEach(k => {
                        if (k !== word) {
                            markdown.appendMarkdown(`- \`${k}\`\n`);
                        }
                    });
                    
                    markdown.appendMarkdown(`\n### Alternative Magic Schools:\n`);
                    for (const [otherSchool, otherKeywords] of Object.entries(variants)) {
                        if (otherSchool !== school) {
                            const otherSchoolInfo = MAGIC_SCHOOLS[otherSchool as keyof typeof MAGIC_SCHOOLS];
                            markdown.appendMarkdown(`**${otherSchoolInfo.icon} ${otherSchoolInfo.name}:** ${otherKeywords.join(', ')}\n\n`);
                        }
                    }
                    
                    return new vscode.Hover(markdown);
                }
            }
        }
        
        return null;
    }
}

export function activate(context: vscode.ExtensionContext) {
    
    // Register completion provider
    const completionProvider = vscode.languages.registerCompletionItemProvider(
        'grimoire',
        new GrimoireCompletionProvider(),
        ...'abcdefghijklmnopqrstuvwxyz'.split('')
    );
    
    // Register hover provider
    const hoverProvider = vscode.languages.registerHoverProvider(
        'grimoire',
        new GrimoireHoverProvider()
    );
    
    // Register commands
    const showVariantsCommand = vscode.commands.registerCommand('grimoire.showKeywordVariants', () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return;
        }
        
        const selection = editor.selection;
        const selectedText = editor.document.getText(selection).toLowerCase();
        
        // Find variants for selected keyword
        for (const [baseKeyword, variants] of Object.entries(KEYWORD_VARIANTS)) {
            for (const [school, keywords] of Object.entries(variants)) {
                if (keywords.includes(selectedText)) {
                    // Show quick pick with all variants
                    const items: vscode.QuickPickItem[] = [];
                    
                    for (const [variantSchool, variantKeywords] of Object.entries(variants)) {
                        const schoolInfo = MAGIC_SCHOOLS[variantSchool as keyof typeof MAGIC_SCHOOLS];
                        variantKeywords.forEach(keyword => {
                            items.push({
                                label: `${schoolInfo.icon} ${keyword}`,
                                description: schoolInfo.name,
                                detail: `${schoolInfo.name} variant of ${baseKeyword}`
                            });
                        });
                    }
                    
                    vscode.window.showQuickPick(items, {
                        title: `Thematic variants for "${selectedText}"`,
                        placeHolder: 'Choose a magical style...'
                    }).then(selected => {
                        if (selected && editor) {
                            const keyword = selected.label.split(' ')[1]; // Remove emoji
                            editor.edit(editBuilder => {
                                editBuilder.replace(selection, keyword);
                            });
                        }
                    });
                    
                    return;
                }
            }
        }
        
        vscode.window.showInformationMessage('No thematic variants found for selected text.');
    });
    
    context.subscriptions.push(completionProvider, hoverProvider, showVariantsCommand);
    
    // Show welcome message
    vscode.window.showInformationMessage(
        '🧙‍♂️ Grimoire Language Support activated! Type any keyword to see magical alternatives.',
        'Show Example',
        'Learn More'
    ).then(selection => {
        if (selection === 'Show Example') {
            vscode.workspace.openTextDocument({
                content: `# Welcome to Grimoire! 🧙‍♂️
# Try typing these keywords and see the magical suggestions:

# Type "bind" to see: bless, curse, inscribe, grow...
bind health = 100

# Type "scry" to see: illuminate, whisper, divine, sing...  
scry $SCROLL(Hello magical world!)

# Type "ritual" to see: blessing, curse, formula, song...
ritual greet():
    illuminate $SCROLL(Welcome to magical programming!)

# Hover over any keyword to see thematic alternatives!
`,
                language: 'grimoire'
            }).then(doc => {
                vscode.window.showTextDocument(doc);
            });
        }
    });
}

export function deactivate() {}