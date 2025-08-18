from typing import TypedDict


class CategoriaSeed(TypedDict, total=False):
    nome: str
    descricao: str
    cor: str
    icone: str
    subcategorias: list["CategoriaSeed"]


CATEGORIAS_SEED = [
    # ALIMENTAÇÃO
    {
        "nome": "Alimentação",
        "descricao": "Gastos relacionados a comida e bebidas",
        "cor": "#FF6B6B",
        "icone": "utensils",
        "subcategorias": [
            {
                "nome": "Supermercado",
                "descricao": "Compras de mercado, feira",
                "cor": "#FF8E8E",
                "icone": "shopping-cart",
            },
            {
                "nome": "Restaurantes",
                "descricao": "Refeições em restaurantes",
                "cor": "#FF9999",
                "icone": "restaurant",
            },
            {
                "nome": "Fast Food",
                "descricao": "Lanches rápidos, delivery",
                "cor": "#FFA4A4",
                "icone": "hamburger",
            },
            {
                "nome": "Padaria",
                "descricao": "Pães, doces, café da manhã",
                "cor": "#FFAFAF",
                "icone": "bread-slice",
            },
            {
                "nome": "Bebidas",
                "descricao": "Bebidas alcoólicas e não alcoólicas",
                "cor": "#FFBABA",
                "icone": "wine",
            },
            {
                "nome": "Doces e Sobremesas",
                "descricao": "Docerias, sorveterias",
                "cor": "#FFC5C5",
                "icone": "ice-cream",
            },
        ],
    },
    # TRANSPORTE
    {
        "nome": "Transporte",
        "descricao": "Gastos com deslocamento e veículos",
        "cor": "#4ECDC4",
        "icone": "car",
        "subcategorias": [
            {
                "nome": "Combustível",
                "descricao": "Gasolina, álcool, diesel",
                "cor": "#6ED5CE",
                "icone": "gas-pump",
            },
            {
                "nome": "Transporte Público",
                "descricao": "Ônibus, metrô, trem",
                "cor": "#7EDDD8",
                "icone": "bus",
            },
            {
                "nome": "Táxi/Uber",
                "descricao": "Corridas de aplicativo e táxi",
                "cor": "#8EE5E2",
                "icone": "taxi",
            },
            {
                "nome": "Estacionamento",
                "descricao": "Zona azul, estacionamentos pagos",
                "cor": "#9EEDEC",
                "icone": "parking",
            },
            {
                "nome": "Manutenção Veículo",
                "descricao": "Mecânico, peças, revisão",
                "cor": "#AEF5F6",
                "icone": "wrench",
            },
            {
                "nome": "Pedágio",
                "descricao": "Pedágios de estradas",
                "cor": "#BEFDFF",
                "icone": "road",
            },
            {
                "nome": "Seguro Veículo",
                "descricao": "Seguro do carro/moto",
                "cor": "#CEFFFF",
                "icone": "shield",
            },
        ],
    },
    # MORADIA
    {
        "nome": "Moradia",
        "descricao": "Gastos com habitação e manutenção da casa",
        "cor": "#45B7D1",
        "icone": "home",
        "subcategorias": [
            {
                "nome": "Aluguel",
                "descricao": "Aluguel mensal da residência",
                "cor": "#5CC1D7",
                "icone": "key",
            },
            {
                "nome": "Condomínio",
                "descricao": "Taxa condominial",
                "cor": "#73CBDD",
                "icone": "building",
            },
            {
                "nome": "Energia Elétrica",
                "descricao": "Conta de luz",
                "cor": "#8AD5E3",
                "icone": "zap",
            },
            {
                "nome": "Água e Esgoto",
                "descricao": "Conta de água",
                "cor": "#A1DFE9",
                "icone": "droplet",
            },
            {
                "nome": "Internet/TV",
                "descricao": "Internet, TV por assinatura",
                "cor": "#B8E9EF",
                "icone": "wifi",
            },
            {
                "nome": "Gás",
                "descricao": "Gás encanado ou botijão",
                "cor": "#CFF3F5",
                "icone": "flame",
            },
            {
                "nome": "Reformas",
                "descricao": "Obras, pinturas, melhorias",
                "cor": "#E6FDFB",
                "icone": "hammer",
            },
            {
                "nome": "Móveis e Decoração",
                "descricao": "Móveis, decorações, utensílios",
                "cor": "#F3FFFE",
                "icone": "sofa",
            },
        ],
    },
    # SAÚDE
    {
        "nome": "Saúde",
        "descricao": "Gastos com cuidados médicos e bem-estar",
        "cor": "#96CEB4",
        "icone": "heart",
        "subcategorias": [
            {
                "nome": "Consultas Médicas",
                "descricao": "Consultas, especialistas",
                "cor": "#A6D6C2",
                "icone": "stethoscope",
            },
            {
                "nome": "Medicamentos",
                "descricao": "Remédios, farmácia",
                "cor": "#B6DED0",
                "icone": "pill",
            },
            {
                "nome": "Exames",
                "descricao": "Exames laboratoriais, imagem",
                "cor": "#C6E6DE",
                "icone": "clipboard",
            },
            {
                "nome": "Plano de Saúde",
                "descricao": "Mensalidade do plano",
                "cor": "#D6EEEC",
                "icone": "shield-heart",
            },
            {
                "nome": "Dentista",
                "descricao": "Tratamentos dentários",
                "cor": "#E6F6FA",
                "icone": "tooth",
            },
            {
                "nome": "Academia/Esportes",
                "descricao": "Mensalidades, personal trainer",
                "cor": "#F6FEFF",
                "icone": "dumbbell",
            },
            {
                "nome": "Terapias",
                "descricao": "Psicólogo, fisioterapeuta",
                "cor": "#FFFFFF",
                "icone": "brain",
            },
        ],
    },
    # EDUCAÇÃO
    {
        "nome": "Educação",
        "descricao": "Gastos com aprendizado e desenvolvimento",
        "cor": "#FECA57",
        "icone": "book",
        "subcategorias": [
            {
                "nome": "Mensalidade Escolar",
                "descricao": "Escola, universidade",
                "cor": "#FED269",
                "icone": "graduation-cap",
            },
            {
                "nome": "Cursos",
                "descricao": "Cursos livres, profissionalizantes",
                "cor": "#FEDA7B",
                "icone": "monitor",
            },
            {
                "nome": "Livros",
                "descricao": "Livros, apostilas",
                "cor": "#FEE28D",
                "icone": "book-open",
            },
            {
                "nome": "Material Escolar",
                "descricao": "Cadernos, canetas, uniformes",
                "cor": "#FEEA9F",
                "icone": "pencil",
            },
            {
                "nome": "Idiomas",
                "descricao": "Cursos de inglês, espanhol, etc",
                "cor": "#FEF2B1",
                "icone": "globe",
            },
            {
                "nome": "Tecnologia",
                "descricao": "Cursos online, plataformas",
                "cor": "#FEFAC3",
                "icone": "laptop",
            },
        ],
    },
    # LAZER E ENTRETENIMENTO
    {
        "nome": "Lazer",
        "descricao": "Diversão, entretenimento e hobbies",
        "cor": "#A29BFE",
        "icone": "smile",
        "subcategorias": [
            {
                "nome": "Cinema/Teatro",
                "descricao": "Ingressos, pipoca",
                "cor": "#B2ACFE",
                "icone": "film",
            },
            {
                "nome": "Shows/Eventos",
                "descricao": "Concerts, festivais",
                "cor": "#C2BDFE",
                "icone": "music",
            },
            {
                "nome": "Streaming",
                "descricao": "Netflix, Spotify, etc",
                "cor": "#D2CEFE",
                "icone": "play",
            },
            {
                "nome": "Jogos",
                "descricao": "Videogames, jogos mobile",
                "cor": "#E2DFFE",
                "icone": "gamepad-2",
            },
            {
                "nome": "Hobbies",
                "descricao": "Materiais para hobbies",
                "cor": "#F2F0FF",
                "icone": "palette",
            },
            {
                "nome": "Viagens",
                "descricao": "Passeios, hospedagem, turismo",
                "cor": "#FFFFFF",
                "icone": "plane",
            },
            {
                "nome": "Esportes",
                "descricao": "Ingressos, equipamentos esportivos",
                "cor": "#F8F7FF",
                "icone": "football",
            },
        ],
    },
    # VESTUÁRIO
    {
        "nome": "Vestuário",
        "descricao": "Roupas, calçados e acessórios",
        "cor": "#FD79A8",
        "icone": "shirt",
        "subcategorias": [
            {
                "nome": "Roupas",
                "descricao": "Camisetas, calças, vestidos",
                "cor": "#FD8BB3",
                "icone": "tshirt",
            },
            {
                "nome": "Calçados",
                "descricao": "Sapatos, tênis, sandálias",
                "cor": "#FD9DBE",
                "icone": "shoe-prints",
            },
            {
                "nome": "Acessórios",
                "descricao": "Bolsas, cintos, joias",
                "cor": "#FDAFC9",
                "icone": "watch",
            },
            {
                "nome": "Roupas Íntimas",
                "descricao": "Lingerie, meias",
                "cor": "#FDC1D4",
                "icone": "heart",
            },
            {
                "nome": "Roupas de Cama",
                "descricao": "Lençóis, cobertores",
                "cor": "#FDD3DF",
                "icone": "bed",
            },
        ],
    },
    # TECNOLOGIA
    {
        "nome": "Tecnologia",
        "descricao": "Eletrônicos, software e serviços digitais",
        "cor": "#6C5CE7",
        "icone": "smartphone",
        "subcategorias": [
            {
                "nome": "Celular",
                "descricao": "Aparelhos, acessórios",
                "cor": "#7D6FE8",
                "icone": "phone",
            },
            {
                "nome": "Computador",
                "descricao": "PCs, notebooks, periféricos",
                "cor": "#8E82E9",
                "icone": "laptop",
            },
            {
                "nome": "Software",
                "descricao": "Aplicativos, licenças",
                "cor": "#9F95EA",
                "icone": "download",
            },
            {
                "nome": "Eletrônicos",
                "descricao": "TV, som, eletrodomésticos",
                "cor": "#B0A8EB",
                "icone": "tv",
            },
            {
                "nome": "Consertos",
                "descricao": "Reparos de eletrônicos",
                "cor": "#C1BBEC",
                "icone": "tool",
            },
        ],
    },
    # TRABALHO
    {
        "nome": "Trabalho",
        "descricao": "Gastos relacionados à atividade profissional",
        "cor": "#00B894",
        "icone": "briefcase",
        "subcategorias": [
            {
                "nome": "Transporte para Trabalho",
                "descricao": "Deslocamento ao trabalho",
                "cor": "#1CC9A6",
                "icone": "bus",
            },
            {
                "nome": "Alimentação no Trabalho",
                "descricao": "Almoço, café",
                "cor": "#38DAB8",
                "icone": "coffee",
            },
            {
                "nome": "Material de Escritório",
                "descricao": "Canetas, papéis",
                "cor": "#54EBCA",
                "icone": "paperclip",
            },
            {
                "nome": "Roupas de Trabalho",
                "descricao": "Uniformes, ternos",
                "cor": "#70FCDC",
                "icone": "user-tie",
            },
            {
                "nome": "Cursos Profissionais",
                "descricao": "Capacitação, certificações",
                "cor": "#8CFFEE",
                "icone": "award",
            },
        ],
    },
    # IMPOSTOS E TAXAS
    {
        "nome": "Impostos",
        "descricao": "Impostos, taxas governamentais",
        "cor": "#E17055",
        "icone": "file-text",
        "subcategorias": [
            {
                "nome": "IPTU",
                "descricao": "Imposto predial",
                "cor": "#E5826B",
                "icone": "home",
            },
            {
                "nome": "IPVA",
                "descricao": "Imposto do veículo",
                "cor": "#E99481",
                "icone": "car",
            },
            {
                "nome": "IR",
                "descricao": "Imposto de renda",
                "cor": "#EDA697",
                "icone": "calculator",
            },
            {
                "nome": "Multas",
                "descricao": "Multas de trânsito",
                "cor": "#F1B8AD",
                "icone": "alert-triangle",
            },
            {
                "nome": "Licenciamento",
                "descricao": "Licenciamento veicular",
                "cor": "#F5CAC3",
                "icone": "file",
            },
        ],
    },
    # INVESTIMENTOS
    {
        "nome": "Investimentos",
        "descricao": "Aplicações financeiras e investimentos",
        "cor": "#00CEC9",
        "icone": "trending-up",
        "subcategorias": [
            {
                "nome": "Poupança",
                "descricao": "Depósitos na poupança",
                "cor": "#1DD8D3",
                "icone": "piggy-bank",
            },
            {
                "nome": "CDB/CDI",
                "descricao": "Certificados de depósito",
                "cor": "#3AE2DD",
                "icone": "bank",
            },
            {
                "nome": "Ações",
                "descricao": "Compra de ações",
                "cor": "#57ECE7",
                "icone": "bar-chart",
            },
            {
                "nome": "Fundos",
                "descricao": "Fundos de investimento",
                "cor": "#74F6F1",
                "icone": "pie-chart",
            },
            {
                "nome": "Criptomoedas",
                "descricao": "Bitcoin, outras cryptos",
                "cor": "#91FFFF",
                "icone": "bitcoin",
            },
        ],
    },
    # CUIDADOS PESSOAIS
    {
        "nome": "Cuidados Pessoais",
        "descricao": "Beleza, higiene e cuidados pessoais",
        "cor": "#FD79A8",
        "icone": "user",
        "subcategorias": [
            {
                "nome": "Cabeleireiro",
                "descricao": "Cortes, tratamentos capilares",
                "cor": "#FD8BB3",
                "icone": "scissors",
            },
            {
                "nome": "Produtos de Beleza",
                "descricao": "Cosméticos, maquiagem",
                "cor": "#FD9DBE",
                "icone": "sparkles",
            },
            {
                "nome": "Produtos de Higiene",
                "descricao": "Sabonetes, shampoo",
                "cor": "#FDAFC9",
                "icone": "droplet",
            },
            {
                "nome": "Manicure/Pedicure",
                "descricao": "Cuidados com unhas",
                "cor": "#FDC1D4",
                "icone": "hand",
            },
            {
                "nome": "Perfumes",
                "descricao": "Fragrâncias, desodorantes",
                "cor": "#FDD3DF",
                "icone": "spray-can",
            },
        ],
    },
    # PETS
    {
        "nome": "Pets",
        "descricao": "Gastos com animais de estimação",
        "cor": "#FDCB6E",
        "icone": "heart",
        "subcategorias": [
            {
                "nome": "Veterinário",
                "descricao": "Consultas, vacinas",
                "cor": "#FDD485",
                "icone": "stethoscope",
            },
            {
                "nome": "Ração",
                "descricao": "Alimentação dos pets",
                "cor": "#FEDD9C",
                "icone": "bone",
            },
            {
                "nome": "Medicamentos Pet",
                "descricao": "Remédios para animais",
                "cor": "#FEE6B3",
                "icone": "pill",
            },
            {
                "nome": "Acessórios Pet",
                "descricao": "Coleiras, brinquedos",
                "cor": "#FEEFCA",
                "icone": "gift",
            },
            {
                "nome": "Petshop",
                "descricao": "Banho, tosa",
                "cor": "#FEF8E1",
                "icone": "scissors",
            },
        ],
    },
    # DIVERSOS/OUTROS
    {
        "nome": "Outros",
        "descricao": "Gastos diversos não categorizados",
        "cor": "#74B9FF",
        "icone": "more-horizontal",
        "subcategorias": [
            {
                "nome": "Presentes",
                "descricao": "Presentes para terceiros",
                "cor": "#85C5FF",
                "icone": "gift",
            },
            {
                "nome": "Doações",
                "descricao": "Contribuições, caridade",
                "cor": "#96D1FF",
                "icone": "heart-handshake",
            },
            {
                "nome": "Empréstimos",
                "descricao": "Pagamento de empréstimos",
                "cor": "#A7DDFF",
                "icone": "hand-coins",
            },
            {
                "nome": "Emergências",
                "descricao": "Gastos emergenciais",
                "cor": "#B8E9FF",
                "icone": "alert-circle",
            },
            {
                "nome": "Não Classificado",
                "descricao": "Gastos a classificar",
                "cor": "#C9F5FF",
                "icone": "help-circle",
            },
        ],
    },
]
